# Attack Vector Threat Map

A Streamlit prototype for mapping illustrative enterprise attack paths, comparing relative risk, and organizing defence-planning discussions.

## Run

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Use

- Adjust each attack vector's likelihood, business impact, and exposure from 1 to 5.
- The planning score is `(likelihood × impact × exposure) / 125 × 100`, rounded to an integer.
- Review the graph, ranked priorities, high-level scenario descriptions, and JSON export.

Scores and paths are illustrative hypotheses, not confirmed vulnerabilities or exploit chains. Validate assumptions with asset owners, control evidence, and organization-specific threat intelligence before using them for investment decisions. The optional AI drafting prompt is provided for use with an approved assistant; the app itself does not connect to an AI service.