
import streamlit as st
import pandas as pd
from dataclasses import dataclass
from typing import Dict
from io import BytesIO
from datetime import datetime

# =========================================================
# Biothermodata V1.3
# Biomass heating value and thermodynamic property calculator
# Stable Streamlit layout, no blank panels
# =========================================================

T0 = 298.15  # K

S_O2 = 0.205
S_CO2 = 0.214
S_H2O_L = 0.070
S_N2 = 0.192
S_SO2 = 0.249

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

    x = C / 12.0
    y = H
    z = O / 16.0
    a = N / 14.0
    b = S / 32.0

    rd_raw = (8 * C + 24 * H - 3 * O + 3 * S) / 24.0
    RD = round(rd_raw, 2)

    hhv_raw = 0.734 * rd_raw - 0.276 * ash + 6.801
    HHV = round(hhv_raw, 2)

    dH = round(-HHV, 2)

    S_biomass_raw = (
        0.0055 * C
        + 0.0954 * H
        + 0.0096 * O
        + 0.0098 * N
        + 0.0138 * S
    ) * 24.0
    S_biomass = round(S_biomass_raw, 2)

    o2 = x + y / 4.0 - z / 2.0 + b

    dS_raw = (
        x * S_CO2
        + y / 2.0 * S_H2O_L
        + a / 2.0 * S_N2
        + b * S_SO2
        - o2 * S_O2
        - S_biomass / 1000.0
    ) * 1000.0
    dS = round(dS_raw, 2)

    dG_raw = dH - T0 * dS / 1_000_000.0
    dG = round(dG_raw, 2)

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


def to_word_text(df):
    lines = [
        "Biothermodata",
        "Biomass heating value prediction based on elemental analysis",
        "",
        "Calculation results",
        "",
        df.to_string(index=False),
        "",
        "Model V1.3 | Input: Ash, C, H, O, N, S",
    ]
    return "\n".join(lines).encode("utf-8")


st.set_page_config(
    page_title="Biothermodata",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
:root {
    --blue:#0757c8;
    --deep:#083d91;
    --soft:#f4f8ff;
    --border:#d8e6fb;
    --green:#0b8f47;
    --red:#df1f2d;
    --orange:#f07a00;
    --purple:#7b2cbf;
    --teal:#008c8c;
    --text:#22365f;
}
.block-container {
    padding-top: 0.65rem;
    padding-bottom: 1rem;
    max-width: 1500px;
}
.hero {
    border-radius: 22px;
    padding: 26px 34px;
    margin-bottom: 20px;
    background: linear-gradient(90deg,#ffffff 0%,#f4f9ff 52%,#eef6ff 100%);
    border: 1px solid var(--border);
    box-shadow: 0 10px 32px rgba(0,70,173,.10);
}
.hero-grid {
    display: grid;
    grid-template-columns: 1fr 430px;
    gap: 24px;
    align-items: center;
}
.brand-wrap {
    display: flex;
    align-items: center;
    gap: 22px;
}
.app-logo {
    width: 84px;
    height: 84px;
    border-radius: 22px;
    background: linear-gradient(145deg,#ffffff,#eaf3ff);
    border: 1px solid #c9dcfb;
    display:flex;
    align-items:center;
    justify-content:center;
    box-shadow: 0 8px 22px rgba(0,80,190,.12);
}
.logo-flame {
    font-size: 46px;
    line-height: 1;
}
.brand-title {
    color: var(--blue);
    font-size: 54px;
    font-weight: 900;
    letter-spacing: -1.8px;
    line-height: 1;
}
.brand-subtitle {
    color: #273f6f;
    font-size: 18px;
    margin-top: 12px;
    font-weight: 520;
}
.campus-simple {
    height: 116px;
    position: relative;
    opacity: .78;
}
.campus-simple .base {
    position:absolute;
    right:0;
    bottom:18px;
    width:410px;
    height:2px;
    background:#9fc4f3;
}
.campus-simple .tower {
    position:absolute;
    right:150px;
    bottom:18px;
    width:58px;
    height:104px;
    border:2px solid #82b1ec;
    border-bottom:0;
    border-radius:20px 20px 0 0;
}
.campus-simple .tower::before {
    content:"";
    position:absolute;
    left:19px;
    top:-25px;
    width:17px;
    height:25px;
    border:2px solid #82b1ec;
    border-bottom:0;
    transform:skewX(-6deg);
}
.campus-simple .tower::after {
    content:"";
    position:absolute;
    left:18px;
    top:25px;
    width:17px;
    height:17px;
    border:2px solid #82b1ec;
    border-radius:50%;
}
.campus-simple .building-left,
.campus-simple .building-right {
    position:absolute;
    bottom:18px;
    width:150px;
    height:48px;
    border:2px solid #9fc4f3;
    border-bottom:0;
    background:rgba(255,255,255,.35);
}
.campus-simple .building-left { right:230px; }
.campus-simple .building-right { right:15px; }
.campus-simple .building-left::after,
.campus-simple .building-right::after {
    content:"";
    position:absolute;
    left:12px;
    right:12px;
    top:14px;
    height:18px;
    background: repeating-linear-gradient(90deg, rgba(7,87,200,.23) 0px, rgba(7,87,200,.23) 2px, transparent 2px, transparent 17px);
}
.section-title {
    font-size: 24px;
    font-weight: 850;
    color: var(--blue);
    margin-bottom: 16px;
}
.small-text {
    color:#3d4b66;
    font-size:15px;
    margin-bottom:16px;
}
.result-grid {
    display:grid;
    grid-template-columns: repeat(4, 1fr);
    gap:14px;
    margin-bottom:20px;
}
.card {
    border-radius:16px;
    padding:18px 10px 16px 10px;
    text-align:center;
    border:1px solid #dfe8f5;
    background:#fbfdff;
    min-height:118px;
    box-shadow:0 6px 18px rgba(0,0,0,.035);
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
}
.card-label {
    font-size:15px;
    font-weight:850;
    margin-bottom:10px;
}
.card-value {
    font-size:30px;
    font-weight:900;
    line-height:1.1;
}
.card-unit {
    font-size:15px;
    margin-top:8px;
    color:#253858;
    font-weight:620;
}
.green { color:var(--green); background:linear-gradient(180deg,#fbfffd,#f4fff8); border-color:#ccebd8; }
.red { color:var(--red); background:linear-gradient(180deg,#fffdfd,#fff5f5); border-color:#ffd4d7; }
.blue { color:var(--blue); background:linear-gradient(180deg,#fdfeff,#f4f8ff); border-color:#d2e2ff; }
.purple { color:var(--purple); background:linear-gradient(180deg,#fffefe,#fbf7ff); border-color:#ead9ff; }
.orange { color:var(--orange); background:linear-gradient(180deg,#fffefd,#fff8ee); border-color:#ffe0bd; }
.teal { color:var(--teal); background:linear-gradient(180deg,#fdffff,#f0ffff); border-color:#cceeee; }
.check { color:var(--green); background:linear-gradient(180deg,#fbfffd,#f1fff6); border-color:#bfeccc; }
.stButton button {
    background:linear-gradient(90deg,#0757c8,#0969da) !important;
    color:white !important;
    border-radius:12px !important;
    border:none !important;
    font-weight:850 !important;
    font-size:18px !important;
    height:60px !important;
    width:100% !important;
}
.stButton button:hover {
    background:linear-gradient(90deg,#003f9e,#0058c8) !important;
    color:white !important;
    border:none !important;
}
.stDownloadButton button {
    border-radius:10px !important;
    font-weight:760 !important;
}
[data-testid="stDataFrame"] {
    text-align:center;
}
[data-testid="stDataFrame"] div {
    text-align:center;
}
.footer {
    margin-top:16px;
    border-top:1px solid #dce7f7;
    padding:18px 6px 8px 6px;
    color:#425475;
    font-size:14px;
    text-align:center;
}
.footer b { color:var(--blue); }
@media (max-width:1100px) {
    .hero-grid { grid-template-columns:1fr; }
    .campus-simple { display:none; }
    .result-grid { grid-template-columns:repeat(2,1fr); }
    .brand-title { font-size:42px; }
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero">
  <div class="hero-grid">
    <div class="brand-wrap">
      <div class="app-logo"><div class="logo-flame">🔥🌱</div></div>
      <div>
        <div class="brand-title">Biothermodata</div>
        <div class="brand-subtitle">Biomass heating value prediction based on elemental analysis</div>
      </div>
    </div>
    <div class="campus-simple">
      <div class="building-left"></div>
      <div class="tower"></div>
      <div class="building-right"></div>
      <div class="base"></div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["▦  Single calculation", "▦  Batch calculation"])

with tab1:
    left, right = st.columns([1.03, 2.08], gap="large")

    with left:
        with st.container(border=True):
            st.markdown('<div class="section-title">⚗️ 1. Elemental analysis input</div>', unsafe_allow_html=True)
            st.markdown('<div class="small-text">Please input the elemental composition (wt%).</div>', unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                ash = st.number_input("Ash (%)", value=0.24, step=0.01, format="%.2f")
                h = st.number_input("H (%)", value=5.99, step=0.01, format="%.2f")
                n = st.number_input("N (%)", value=0.39, step=0.01, format="%.2f")
            with c2:
                c = st.number_input("C (%)", value=42.76, step=0.01, format="%.2f")
                o = st.number_input("O (%)", value=50.62, step=0.01, format="%.2f")
                s = st.number_input("S (%)", value=0.00, step=0.01, format="%.2f")

            total = ash + c + h + o + n + s
            status_text = "Qualified" if abs(total - 100) <= 1 else "Check input"
            st.button("▣  Calculate thermodynamic parameters", type="primary")

    with right:
        with st.container(border=True):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.markdown(
                f'<div class="section-title">📊 2. Thermodynamic parameters <span style="float:right;font-size:14px;color:#5d6b89;font-weight:600;">◷ {now}</span></div>',
                unsafe_allow_html=True,
            )

            result = calculate_biomass_thermo(BiomassInput(ash, c, h, o, n, s))
            result_df = pd.DataFrame([{
                "Ash (%)": ash,
                "C (%)": c,
                "H (%)": h,
                "O (%)": o,
                "N (%)": n,
                "S (%)": s,
                **result,
            }])

            st.markdown(
                f"""
<div class="result-grid">
  <div class="card green">
    <div class="card-label">Reduction Degree (RD)</div>
    <div class="card-value">{result['RD']:.2f}</div>
    <div class="card-unit">–</div>
  </div>
  <div class="card red">
    <div class="card-label">Higher Heating Value (HHV)</div>
    <div class="card-value">{result['HHV (MJ/kg)']:.2f}</div>
    <div class="card-unit">MJ/kg</div>
  </div>
  <div class="card blue">
    <div class="card-label">ΔrH°</div>
    <div class="card-value">{result['ΔrH° (MJ/kg)']:.2f}</div>
    <div class="card-unit">MJ/kg</div>
  </div>
  <div class="card purple">
    <div class="card-label">Standard Entropy (S°)</div>
    <div class="card-value">{result['S° (J/(kg·K))']:.2f}</div>
    <div class="card-unit">J/(kg·K)</div>
  </div>
  <div class="card orange">
    <div class="card-label">ΔrS°</div>
    <div class="card-value">{result['ΔrS° (J/(kg·K))']:.2f}</div>
    <div class="card-unit">J/(kg·K)</div>
  </div>
  <div class="card teal">
    <div class="card-label">ΔrG°</div>
    <div class="card-value">{result['ΔrG° (MJ/kg)']:.2f}</div>
    <div class="card-unit">MJ/kg</div>
  </div>
  <div class="card blue">
    <div class="card-label">Chemical Exergy</div>
    <div class="card-value">{result['Exergy (MJ/kg)']:.2f}</div>
    <div class="card-unit">MJ/kg</div>
  </div>
  <div class="card check">
    <div class="card-label">Elemental Check</div>
    <div class="card-value" style="font-size:27px;">{total:.2f}%</div>
    <div class="card-unit">{status_text}</div>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

            st.markdown("#### ▦ Detailed results")
            st.dataframe(result_df, use_container_width=True, hide_index=True)

            b1, b2, b3 = st.columns([1, 1, 1])
            with b1:
                st.download_button(
                    label="⬇ Download as Excel",
                    data=to_excel(result_df),
                    file_name="biothermodata_result.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            with b2:
                st.download_button(
                    label="⬇ Download as Word",
                    data=to_word_text(result_df),
                    file_name="biothermodata_result.doc",
                    mime="application/msword",
                )
            with b3:
                st.download_button(
                    label="⬇ Download as CSV",
                    data=result_df.to_csv(index=False).encode("utf-8-sig"),
                    file_name="biothermodata_result.csv",
                    mime="text/csv",
                )

with tab2:
    with st.container(border=True):
        st.markdown('<div class="section-title">📁 Batch calculation</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-text">Input or upload elemental analysis data. Required columns: Ash, C, H, O, N, S.</div>', unsafe_allow_html=True)

        example_df = pd.DataFrame({
            "Ash": [0.00, 0.10, 0.15, 0.24],
            "C": [44.02, 50.90, 46.89, 42.76],
            "H": [6.80, 5.99, 5.90, 5.99],
            "O": [47.77, 42.90, 46.07, 50.62],
            "N": [1.41, 0.10, 0.61, 0.39],
            "S": [0.00, 0.01, 0.37, 0.00],
        })

        input_df = st.data_editor(
            example_df,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
        )

        uploaded_file = st.file_uploader("Upload an Excel/CSV file", type=["xlsx", "csv"])

        if uploaded_file is not None:
            if uploaded_file.name.lower().endswith(".csv"):
                input_df = pd.read_csv(uploaded_file)
            else:
                input_df = pd.read_excel(uploaded_file)
            st.success("File uploaded successfully.")
            st.dataframe(input_df, use_container_width=True, hide_index=True)

        required_cols = ["Ash", "C", "H", "O", "N", "S"]

        if st.button("▣  Calculate batch results", type="primary"):
            missing_cols = [col for col in required_cols if col not in input_df.columns]
            if missing_cols:
                st.error(f"Missing required columns: {', '.join(missing_cols)}")
            else:
                results = []
                for _, row in input_df.iterrows():
                    calculated = calculate_row(row)
                    results.append({**row.to_dict(), **calculated})

                result_df = pd.DataFrame(results)
                st.markdown("#### ▦ Batch thermodynamic results")
                st.dataframe(result_df, use_container_width=True, hide_index=True)

                b1, b2, b3 = st.columns([1, 1, 1])
                with b1:
                    st.download_button(
                        label="⬇ Download batch as Excel",
                        data=to_excel(result_df),
                        file_name="biothermodata_batch_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                with b2:
                    st.download_button(
                        label="⬇ Download batch as Word",
                        data=to_word_text(result_df),
                        file_name="biothermodata_batch_results.doc",
                        mime="application/msword",
                    )
                with b3:
                    st.download_button(
                        label="⬇ Download batch as CSV",
                        data=result_df.to_csv(index=False).encode("utf-8-sig"),
                        file_name="biothermodata_batch_results.csv",
                        mime="text/csv",
                    )

st.markdown(
    """
<div class="footer">
  <b>Biothermodata</b> &nbsp; | &nbsp; Model V1.3 &nbsp; | &nbsp; © 2025 Nanjing Tech University
</div>
""",
    unsafe_allow_html=True,
)
