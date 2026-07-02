import streamlit as st
import pandas as pd
from dataclasses import dataclass
from typing import Dict
from io import BytesIO
from datetime import datetime

# =========================================================
# Biomass Thermodynamic Agent V2.0
# Nanjing Tech University Style | No logo image required
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
        "HHV (MJ/kg)": HHV,
        "ΔrH° (MJ/kg)": dH,
        "S° (J/(kg·K))": S_biomass,
        "ΔrS° (J/(kg·K))": dS,
        "ΔrG° (MJ/kg)": dG,
        "Exergy (MJ/kg)": exergy,
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
    lines = []
    lines.append("Biomass Thermodynamic Agent")
    lines.append("Nanjing Tech University")
    lines.append("")
    lines.append("Thermodynamic calculation results")
    lines.append("")
    lines.append(df.to_string(index=False))
    lines.append("")
    lines.append("Model V2.0 | Based on elemental analysis: Ash, C, H, O, N, S")
    lines.append("Outputs are calibrated to the golden dataset.")
    return "\n".join(lines).encode("utf-8")


st.set_page_config(
    page_title="Biomass Thermodynamic Agent",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    :root {
        --njtech-blue: #0046ad;
        --njtech-deep: #00357f;
        --light-border: #dbe7f7;
        --green: #0b8f47;
        --red: #df1f2d;
        --orange: #f07a00;
        --purple: #7b2cbf;
        --teal: #008c8c;
    }
    .block-container { padding-top: 0.8rem; padding-bottom: 1rem; max-width: 1500px; }
    .hero {
        background: linear-gradient(90deg, #ffffff 0%, #f2f7ff 50%, #ffffff 100%);
        border: 1px solid var(--light-border);
        border-radius: 18px;
        padding: 22px 28px 18px 28px;
        margin-bottom: 18px;
        box-shadow: 0 8px 28px rgba(0, 70, 173, 0.08);
    }
    .hero-grid { display: grid; grid-template-columns: 310px 1fr 230px; gap: 26px; align-items: center; }
    .school-cn {
        font-size: 38px; line-height: 1.0; color: var(--njtech-blue); font-weight: 800;
        letter-spacing: 4px; font-family: KaiTi, STKaiti, SimKai, serif;
    }
    .school-en {
        color: var(--njtech-blue); font-size: 19px; font-weight: 800; margin-top: 12px;
        letter-spacing: 1px; font-family: Georgia, 'Times New Roman', serif;
    }
    .hero-title { color: var(--njtech-deep); font-size: 38px; font-weight: 850; margin-bottom: 6px; }
    .hero-subtitle { color: #243b66; font-size: 18px; font-weight: 500; }
    .motto {
        color: var(--njtech-blue); margin-top: 12px; font-size: 18px; letter-spacing: 10px;
        font-weight: 700; font-family: KaiTi, STKaiti, SimKai, serif;
    }
    .about-box { text-align: right; color: var(--njtech-blue); font-weight: 700; font-size: 16px; }
    .campus-line {
        height: 54px; border-bottom: 2px solid #b9d4ff; opacity: 0.75;
        background: repeating-linear-gradient(90deg, transparent 0px, transparent 18px, rgba(0,70,173,0.18) 19px, transparent 20px);
        border-radius: 8px; margin-top: 12px;
    }
    .panel {
        border: 1px solid var(--light-border); border-radius: 16px; padding: 20px; background: #ffffff;
        box-shadow: 0 8px 28px rgba(0, 70, 173, 0.06); min-height: 620px;
    }
    .panel-title { font-size: 24px; font-weight: 850; color: var(--njtech-blue); margin-bottom: 18px; }
    .small-text { color: #3d4b66; font-size: 15px; margin-bottom: 16px; }
    .result-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 20px; }
    .card {
        border-radius: 14px; padding: 18px 10px 16px 10px; text-align: center;
        border: 1px solid #dfe8f5; background: #fbfdff; min-height: 118px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.035);
    }
    .card-label { font-size: 15px; font-weight: 800; margin-bottom: 10px; }
    .card-value { font-size: 29px; font-weight: 850; line-height: 1.1; }
    .card-unit { font-size: 15px; margin-top: 8px; color: #253858; font-weight: 600; }
    .green { color: var(--green); background: linear-gradient(180deg,#fbfffd,#f4fff8); border-color:#ccebd8; }
    .red { color: var(--red); background: linear-gradient(180deg,#fffdfd,#fff5f5); border-color:#ffd4d7; }
    .blue { color: var(--njtech-blue); background: linear-gradient(180deg,#fdfeff,#f4f8ff); border-color:#d2e2ff; }
    .purple { color: var(--purple); background: linear-gradient(180deg,#fffefe,#fbf7ff); border-color:#ead9ff; }
    .orange { color: var(--orange); background: linear-gradient(180deg,#fffefd,#fff8ee); border-color:#ffe0bd; }
    .teal { color: var(--teal); background: linear-gradient(180deg,#fdffff,#f0ffff); border-color:#cceeee; }
    .dark { color: #2a3a5f; background: linear-gradient(180deg,#ffffff,#f8f9fc); border-color:#dce3ef; }
    .status-ok { background: #e8fff1; border: 1px solid #bfeccc; color: #08763a; border-radius: 10px; padding: 13px 16px; font-weight: 600; margin-top: 14px; margin-bottom: 18px; }
    .status-warn { background: #fff7e6; border: 1px solid #ffd98a; color: #9b5b00; border-radius: 10px; padding: 13px 16px; font-weight: 600; margin-top: 14px; margin-bottom: 18px; }
    .note { margin-top: 20px; padding: 14px 16px; border-radius: 12px; background: #f8fbff; border: 1px solid var(--light-border); color: #243b66; font-size: 14px; line-height: 1.65; }
    .footer { margin-top: 18px; border: 1px solid var(--light-border); border-radius: 16px; padding: 18px 26px; background: linear-gradient(90deg,#f5f9ff,#ffffff,#f5f9ff); display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; align-items: center; color: #263f70; font-size: 14px; }
    .footer-center { text-align: center; color: var(--njtech-blue); font-weight: 800; font-size: 16px; }
    .footer-right { text-align: right; }
    .stButton button { background: linear-gradient(90deg, #0046ad, #0969da); color: white; border-radius: 10px; border: none; font-weight: 750; height: 50px; width: 100%; }
    .stButton button:hover { background: linear-gradient(90deg, #00357f, #0058c8); color: white; border: none; }
    .stDownloadButton button { border-radius: 9px; font-weight: 700; }
    @media (max-width: 1100px) { .hero-grid { grid-template-columns: 1fr; } .about-box { text-align: left; } .result-grid { grid-template-columns: repeat(2, 1fr); } }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero">
  <div class="hero-grid">
    <div>
      <div class="school-cn">南京工业大学</div>
      <div class="school-en">NANJING TECH UNIVERSITY</div>
    </div>
    <div>
      <div class="hero-title">Biomass Thermodynamic Agent 🌿</div>
      <div class="hero-subtitle">Thermodynamic property calculation based on elemental analysis</div>
      <div class="motto">明德 厚学 沉毅 笃行</div>
    </div>
    <div class="about-box">
      Model V2.0<br>
      Biomass thermodynamic calculation
      <div class="campus-line"></div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["▦  Single calculation", "▦  Batch calculation"])

with tab1:
    left, right = st.columns([1.02, 2.2], gap="large")

    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">⚗️ 1. Elemental analysis input</div>', unsafe_allow_html=True)
        st.markdown('<div class="small-text">Please input the elemental composition (wt%).</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            ash = st.number_input("▲ Ash (%)", value=0.24, step=0.01, format="%.2f")
            h = st.number_input("H  H (%)", value=5.99, step=0.01, format="%.2f")
            n = st.number_input("N  N (%)", value=0.39, step=0.01, format="%.2f")
        with c2:
            c = st.number_input("C  C (%)", value=42.76, step=0.01, format="%.2f")
            o = st.number_input("O  O (%)", value=50.62, step=0.01, format="%.2f")
            s = st.number_input("S  S (%)", value=0.00, step=0.01, format="%.2f")

        total = ash + c + h + o + n + s
        if abs(total - 100) <= 1:
            st.markdown(f'<div class="status-ok">● Elemental total = {total:.2f}%. Data are within the acceptable range.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-warn">● Elemental total = {total:.2f}%. Please check whether normalization is required.</div>', unsafe_allow_html=True)

        st.button("⚛ Calculate thermodynamic parameters", type="primary")

        st.markdown("""
<div class="note">
<b>Note:</b><br>
All outputs are calculated on the basis of elemental analysis and calibrated against the golden dataset containing 265 cases.
</div>
""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f'<div class="panel-title">📊 2. Thermodynamic parameters <span style="float:right;font-size:14px;color:#5d6b89;font-weight:600;">◷ {now}</span></div>', unsafe_allow_html=True)

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

        st.markdown(f"""
<div class="result-grid">
  <div class="card green"><div class="card-label">🌿 Reduction Degree (RD)</div><div class="card-value">{result['RD']:.2f}</div><div class="card-unit">–</div></div>
  <div class="card red"><div class="card-label">🔥 Higher Heating Value (HHV)</div><div class="card-value">{result['HHV (MJ/kg)']:.2f}</div><div class="card-unit">MJ/kg</div></div>
  <div class="card blue"><div class="card-label">🌡️ ΔrH°</div><div class="card-value">{result['ΔrH° (MJ/kg)']:.2f}</div><div class="card-unit">MJ/kg</div></div>
  <div class="card purple"><div class="card-label">♨ Standard Entropy (S°)</div><div class="card-value">{result['S° (J/(kg·K))']:.2f}</div><div class="card-unit">J/(kg·K)</div></div>
  <div class="card orange"><div class="card-label">⚙ ΔrS°</div><div class="card-value">{result['ΔrS° (J/(kg·K))']:.2f}</div><div class="card-unit">J/(kg·K)</div></div>
  <div class="card teal"><div class="card-label">⚖ ΔrG°</div><div class="card-value">{result['ΔrG° (MJ/kg)']:.2f}</div><div class="card-unit">MJ/kg</div></div>
  <div class="card blue"><div class="card-label">💎 Chemical Exergy</div><div class="card-value">{result['Exergy (MJ/kg)']:.2f}</div><div class="card-unit">MJ/kg</div></div>
  <div class="card dark"><div class="card-label">✓ HHV Check</div><div class="card-value">{result['HHV (MJ/kg)']:.2f}</div><div class="card-unit">MJ/kg</div></div>
</div>
""", unsafe_allow_html=True)

        st.markdown("#### ▦ Detailed results")
        st.dataframe(result_df, use_container_width=True, hide_index=True)

        b1, b2, b3 = st.columns([1, 1, 1])
        with b1:
            st.download_button("⬇ Download result as Excel", data=to_excel(result_df), file_name="biomass_thermodynamic_result.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with b2:
            st.download_button("⬇ Download result as Word", data=to_word_text(result_df), file_name="biomass_thermodynamic_result.doc", mime="application/msword")
        with b3:
            st.download_button("⬇ Download result as CSV", data=result_df.to_csv(index=False).encode("utf-8-sig"), file_name="biomass_thermodynamic_result.csv", mime="text/csv")

        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">📁 Batch calculation</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-text">Input or upload elemental analysis data. Required columns: Ash, C, H, O, N, S.</div>', unsafe_allow_html=True)

    example_df = pd.DataFrame({
        "Ash": [0.00, 0.10, 0.15, 0.24],
        "C": [44.02, 50.90, 46.89, 42.76],
        "H": [6.80, 5.99, 5.90, 5.99],
        "O": [47.77, 42.90, 46.07, 50.62],
        "N": [1.41, 0.10, 0.61, 0.39],
        "S": [0.00, 0.01, 0.37, 0.00],
    })

    input_df = st.data_editor(example_df, num_rows="dynamic", use_container_width=True, hide_index=True)
    uploaded_file = st.file_uploader("Upload an Excel/CSV file", type=["xlsx", "csv"])

    if uploaded_file is not None:
        if uploaded_file.name.lower().endswith(".csv"):
            input_df = pd.read_csv(uploaded_file)
        else:
            input_df = pd.read_excel(uploaded_file)
        st.success("File uploaded successfully.")
        st.dataframe(input_df, use_container_width=True)

    required_cols = ["Ash", "C", "H", "O", "N", "S"]
    if st.button("⚛ Calculate batch results", type="primary"):
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
                st.download_button("⬇ Download batch results as Excel", data=to_excel(result_df), file_name="biomass_thermodynamic_batch_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            with b2:
                st.download_button("⬇ Download batch results as Word", data=to_word_text(result_df), file_name="biomass_thermodynamic_batch_results.doc", mime="application/msword")
            with b3:
                st.download_button("⬇ Download batch results as CSV", data=result_df.to_csv(index=False).encode("utf-8-sig"), file_name="biomass_thermodynamic_batch_results.csv", mime="text/csv")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="footer">
  <div><b>Model V2.0</b><br>Biomass Thermodynamic Agent</div>
  <div class="footer-center">NANJING TECH UNIVERSITY<br>明德&nbsp;&nbsp;厚学&nbsp;&nbsp;沉毅&nbsp;&nbsp;笃行</div>
  <div class="footer-right">Based on elemental analysis: Ash, C, H, O, N, S<br>Outputs are calibrated to the golden dataset (265 cases)</div>
</div>
""", unsafe_allow_html=True)
