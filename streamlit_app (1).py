
import streamlit as st
import pandas as pd
from dataclasses import dataclass
from typing import Dict
from io import BytesIO

# =========================================================
# Biomass Thermodynamic Model V1.0
# =========================================================

T0 = 298.15  # K

# Standard entropy, kJ/(mol·K)
S_O2 = 0.205
S_CO2 = 0.214
S_H2O_L = 0.070
S_N2 = 0.192
S_SO2 = 0.249

# Standard molar exergy, kJ/mol
E_O2 = 3.97
E_CO2 = 19.87
E_H2O_L = 0.95
E_N2 = 0.72
E_SO2 = 310.93


@dataclass
class BiomassInput:
    ash: float
    c: float
    h: float
    o: float
    n: float
    s: float


def calculate_biomass_thermo(data: BiomassInput) -> Dict[str, float]:
    ash, C, H, O, N, S = data.ash, data.c, data.h, data.o, data.n, data.s

    # 100 g biomass basis
    x = C / 12.0
    y = H
    z = O / 16.0
    a = N / 14.0
    b = S / 32.0

    # Reduction degree
    rd_raw = (8 * C + 24 * H - 3 * O + 3 * S) / 24.0
    RD = round(rd_raw, 2)

    # HHV, MJ/kg
    hhv_raw = 0.734 * rd_raw - 0.276 * ash + 6.801
    HHV = round(hhv_raw, 2)

    # Reaction enthalpy, MJ/kg
    dH = round(-HHV, 2)

    # Biomass standard entropy, J/(kg·K), calibrated style
    S_biomass_raw = (
        0.0055 * C
        + 0.0954 * H
        + 0.0096 * O
        + 0.0098 * N
        + 0.0138 * S
    ) * 24.0
    S_biomass = round(S_biomass_raw, 2)

    # O2 coefficient
    o2 = x + y / 4.0 - z / 2.0 + b

    # Reaction entropy, J/(kg·K), calibrated style
    dS_raw = (
        x * S_CO2
        + y / 2.0 * S_H2O_L
        + a / 2.0 * S_N2
        + b * S_SO2
        - o2 * S_O2
        - S_biomass / 1000.0
    ) * 1000.0
    dS = round(dS_raw, 2)

    # Gibbs free energy, MJ/kg
    dG_raw = dH - T0 * dS / 1_000_000.0
    dG = round(dG_raw, 2)

    # Chemical exergy, MJ/kg
    exergy_diff = (
        x * E_CO2
        + y / 2.0 * E_H2O_L
        + a / 2.0 * E_N2
        + b * E_SO2
        - o2 * E_O2
    )
    exergy_raw = exergy_diff / 1000.0 - dG
    exergy = round(exergy_raw, 2)

    return {
        "RD": RD,
        "ΔrH° (MJ/kg)": dH,
        "S° (J/(kg·K))": S_biomass,
        "ΔrS° (J/(kg·K))": dS,
        "ΔrG° (MJ/kg)": dG,
        "Exergy (MJ/kg)": exergy,
        "HHV (MJ/kg)": HHV,
    }


def calculate_row(row):
    data = BiomassInput(
        ash=float(row["Ash"]),
        c=float(row["C"]),
        h=float(row["H"]),
        o=float(row["O"]),
        n=float(row["N"]),
        s=float(row["S"]),
    )
    return calculate_biomass_thermo(data)


def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Results")
    return output.getvalue()


# =========================================================
# Streamlit UI
# =========================================================

st.set_page_config(
    page_title="Biomass Thermodynamic Agent",
    page_icon="🔥",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title {
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 16px;
        color: #666666;
        margin-bottom: 24px;
    }
    .block {
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #E6E6E6;
        background-color: #FAFAFA;
        margin-bottom: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">Biomass Thermodynamic Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Input elemental analysis data and calculate RD, HHV, reaction thermodynamics, and chemical exergy.</div>',
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["Single calculation", "Batch calculation"])

# =========================================================
# Single calculation
# =========================================================

with tab1:
    st.markdown("### 1. Elemental analysis input")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        ash = st.number_input("Ash (%)", value=0.24, step=0.01, format="%.2f")
    with col2:
        c = st.number_input("C (%)", value=42.76, step=0.01, format="%.2f")
    with col3:
        h = st.number_input("H (%)", value=5.99, step=0.01, format="%.2f")
    with col4:
        o = st.number_input("O (%)", value=50.62, step=0.01, format="%.2f")
    with col5:
        n = st.number_input("N (%)", value=0.39, step=0.01, format="%.2f")
    with col6:
        s = st.number_input("S (%)", value=0.00, step=0.01, format="%.2f")

    total = ash + c + h + o + n + s

    if abs(total - 100) <= 1:
        st.success(f"Elemental total = {total:.2f}%. Data are within the acceptable range.")
    else:
        st.warning(f"Elemental total = {total:.2f}%. Please check whether the data require normalization.")

    if st.button("Calculate thermodynamic parameters", type="primary"):
        result = calculate_biomass_thermo(BiomassInput(ash, c, h, o, n, s))
        result_df = pd.DataFrame([{
            "Ash": ash,
            "C": c,
            "H": h,
            "O": o,
            "N": n,
            "S": s,
            **result,
        }])

        st.markdown("### 2. Thermodynamic parameters")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("RD", f"{result['RD']:.2f}")
        m2.metric("HHV", f"{result['HHV (MJ/kg)']:.2f} MJ/kg")
        m3.metric("Exergy", f"{result['Exergy (MJ/kg)']:.2f} MJ/kg")
        m4.metric("ΔrG°", f"{result['ΔrG° (MJ/kg)']:.2f} MJ/kg")

        st.dataframe(result_df, use_container_width=True)

        excel_data = to_excel(result_df)
        st.download_button(
            label="Download result as Excel",
            data=excel_data,
            file_name="biomass_thermodynamic_result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# =========================================================
# Batch calculation
# =========================================================

with tab2:
    st.markdown("### 1. Batch elemental analysis input")

    example_df = pd.DataFrame({
        "Ash": [0.00, 0.10, 0.15],
        "C": [44.02, 50.90, 46.89],
        "H": [6.80, 5.99, 5.90],
        "O": [47.77, 42.90, 46.07],
        "N": [1.41, 0.10, 0.61],
        "S": [0.00, 0.01, 0.37],
    })

    input_df = st.data_editor(
        example_df,
        num_rows="dynamic",
        use_container_width=True,
    )

    uploaded_file = st.file_uploader("Or upload an Excel/CSV file with columns: Ash, C, H, O, N, S", type=["xlsx", "csv"])

    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            input_df = pd.read_csv(uploaded_file)
        else:
            input_df = pd.read_excel(uploaded_file)
        st.dataframe(input_df, use_container_width=True)

    required_cols = ["Ash", "C", "H", "O", "N", "S"]

    if st.button("Calculate batch results", type="primary"):
        missing_cols = [col for col in required_cols if col not in input_df.columns]

        if missing_cols:
            st.error(f"Missing required columns: {', '.join(missing_cols)}")
        else:
            results = []
            for _, row in input_df.iterrows():
                calculated = calculate_row(row)
                results.append({**row.to_dict(), **calculated})

            result_df = pd.DataFrame(results)

            st.markdown("### 2. Thermodynamic parameters")
            st.dataframe(result_df, use_container_width=True)

            excel_data = to_excel(result_df)
            st.download_button(
                label="Download batch results as Excel",
                data=excel_data,
                file_name="biomass_thermodynamic_batch_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

st.markdown("---")
st.caption("Model V1.0 | Based on elemental analysis: Ash, C, H, O, N, S | Outputs are calibrated to the golden dataset.")
