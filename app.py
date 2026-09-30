from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Attack Vector Threat Map",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

VECTORS = [
    {"vector": "Web application", "entry": "Public web app", "technique": "T1190 · Exploit Public-Facing Application", "scenario": "An exposed application flaw is used to gain an initial foothold, then reach an identity or data service.", "likelihood": 4, "impact": 5, "exposure": 5, "control": "Patch cadence · WAF rules · external testing", "owner": "Application security"},
    {"vector": "Email", "entry": "Employee inbox", "technique": "T1566 · Phishing", "scenario": "A convincing message leads a user to disclose credentials or open a malicious attachment; the account is then used to access internal services.", "likelihood": 4, "impact": 4, "exposure": 4, "control": "Phishing-resistant MFA · mail filtering · reporting", "owner": "Identity & email"},
    {"vector": "Mobile device", "entry": "Managed mobile device", "technique": "T1078 · Valid Accounts", "scenario": "A lost, compromised, or poorly governed device exposes an authenticated session or sensitive business data.", "likelihood": 3, "impact": 4, "exposure": 3, "control": "MDM · device encryption · conditional access", "owner": "Endpoint security"},
    {"vector": "Physical access", "entry": "Office / equipment", "technique": "T1200 · Hardware Additions", "scenario": "Unauthorized access to a workspace or unattended equipment creates an opportunity to connect a device or view sensitive information.", "likelihood": 2, "impact": 4, "exposure": 2, "control": "Visitor controls · badge reviews · port security", "owner": "Corporate security"},
    {"vector": "Insider", "entry": "Privileged employee", "technique": "T1078 · Valid Accounts", "scenario": "An over-privileged or compromised workforce account accesses data beyond its business need, intentionally or accidentally.", "likelihood": 3, "impact": 5, "exposure": 3, "control": "Least privilege · access reviews · audit alerts", "owner": "Identity & data"},
    {"vector": "Supply chain", "entry": "Third-party service", "technique": "T1195 · Supply Chain Compromise", "scenario": "A trusted supplier, software dependency, or integration is compromised and becomes a path into a business system.", "likelihood": 3, "impact": 5, "exposure": 4, "control": "Vendor assurance · dependency controls · segmentation", "owner": "Third-party risk"},
]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --ink:#e8edf5; --muted:#8794a9; --line:rgba(154,174,205,.15); --panel:#111a28; --bg:#0b111b; --mint:#57e3bd; }
.stApp { background:radial-gradient(ellipse at 15% -10%, #142b3b 0%, #0b111b 42%); color:var(--ink); font-family:'Manrope',sans-serif; }
[data-testid="stHeader"] { background:transparent; }
[data-testid="stSidebar"] { background:#0e1723; border-right:1px solid var(--line); }
[data-testid="stSidebar"] * { font-family:'Manrope',sans-serif; }
.block-container { padding-top:2.1rem; padding-bottom:3rem; max-width:1500px; }
.eyebrow { color:#65dabb; font:500 11px 'DM Mono',monospace; letter-spacing:.15em; text-transform:uppercase; }
.hero-title { font-size:clamp(34px,4vw,54px); letter-spacing:-.055em; line-height:1.05; font-weight:800; margin:.45rem 0 .6rem; color:#f1f5fb; }
.hero-sub { color:#a5b1c3; font-size:15px; max-width:700px; line-height:1.7; }
.metric-card { background:linear-gradient(135deg,rgba(23,38,54,.94),rgba(16,25,38,.94)); border:1px solid var(--line); border-radius:14px; padding:18px 20px; min-height:112px; }
.metric-label { color:#93a1b4; font:11px 'DM Mono',monospace; letter-spacing:.08em; text-transform:uppercase; }
.metric-value { color:#edf4fb; font-size:29px; font-weight:700; letter-spacing:-.04em; margin-top:8px; }
.metric-note { color:#6edabd; font-size:11px; margin-top:1px; }
.section-title { color:#eaf0f7; font-size:18px; font-weight:700; letter-spacing:-.02em; }
.section-note { color:#8e9bad; font-size:12px; margin-top:-9px; margin-bottom:12px; }
.stTabs [data-baseweb="tab-list"] { gap:18px; border-bottom:1px solid var(--line); }
.stTabs [data-baseweb="tab"] { color:#9ba9bc; height:48px; }
.stTabs [aria-selected="true"] { color:#68dfbe !important; }
div[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.stButton button, .stDownloadButton button { border-radius:8px; }
hr { border-color:var(--line); }
</style>
""", unsafe_allow_html=True)


def score_risk(likelihood: int, impact: int, exposure: int) -> int:
    """Planning score, 0–100: likelihood × impact × exposure, each 1–5."""
    return round((likelihood * impact * exposure / 125) * 100)


def band(score: int) -> str:
    return "Critical" if score >= 75 else "High" if score >= 50 else "Moderate" if score >= 25 else "Lower"


def band_color(score: int) -> str:
    return "#ff6b72" if score >= 75 else "#ffb454" if score >= 50 else "#59d6ba" if score >= 25 else "#71839a"


if "risk_inputs" not in st.session_state:
    st.session_state.risk_inputs = pd.DataFrame(VECTORS)[["vector", "likelihood", "impact", "exposure"]]

with st.sidebar:
    st.markdown("<div class='eyebrow'>FIELDNOTES / SECURITY</div>", unsafe_allow_html=True)
    st.markdown("## ◈ Threat map")
    st.caption("A lightweight workshop tool for attack-path discovery and budget conversations.")
    st.divider()
    st.markdown("**Scoring model**")
    st.caption("Likelihood × impact × exposure, each rated 1–5. The product is normalized to a 0–100 planning score.")
    st.caption("Lower 0–24 · Moderate 25–49 · High 50–74 · Critical 75–100")
    st.info("Scores are comparative workshop estimates. They do not include control effectiveness, threat intelligence, asset criticality weighting, or uncertainty intervals.", icon="💡")
    st.markdown("**Scope**")
    st.caption("Illustrative enterprise scenario. Replace assumptions with asset, control, incident, and threat intelligence from your environment.")
    st.caption("ATT&CK technique names are reference points, not a complete mapping.")
    st.divider()
    st.markdown("**Workshop assumptions**")
    org_name = st.text_input("Organization / scenario", "Northstar Group")
    st.caption("Keep sensitive infrastructure details out of shared or public exports.")

st.markdown("<div class='eyebrow'>CYBERSECURITY · DECISION SUPPORT</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-title'>Attack vector<br>threat map<span style='color:#57e3bd'>.</span></div>", unsafe_allow_html=True)
st.markdown(f"<div class='hero-sub'>Map plausible entry points to business-critical systems, compare relative risk, and turn the discussion into a defence investment shortlist. <span style='color:#d6deea'>{org_name}</span></div>", unsafe_allow_html=True)
st.write("")

edited = st.data_editor(
    st.session_state.risk_inputs,
    key="risk_editor",
    hide_index=True,
    use_container_width=True,
    column_config={
        "vector": st.column_config.TextColumn("Attack vector", disabled=True),
        "likelihood": st.column_config.NumberColumn(
            "Likelihood", min_value=1, max_value=5, step=1
        ),
        "impact": st.column_config.NumberColumn(
            "Business impact", min_value=1, max_value=5, step=1
        ),
        "exposure": st.column_config.NumberColumn(
            "Exposure", min_value=1, max_value=5, step=1
        ),
    },
)
st.session_state.risk_inputs = edited