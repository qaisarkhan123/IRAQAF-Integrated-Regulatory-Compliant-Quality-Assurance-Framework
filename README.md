
# IRAQAF Starter Kit (Research Toolkit → App-ready)

This repo is a minimal, modular scaffold to evaluate AI systems across five modules:

- L1 Governance & Regulatory (CRS)
- L2 Privacy & Security (SAI)
- L3 Fairness (FI)
- L4 Explainability & Transparency (TS)
- L5 Ops & Monitoring (Ops)

## Quick start
```bash
pip install -r requirements.txt

# Run a module
python -m cli.iraqaf_cli run --module L3 --config configs/fairness.example.yaml --out reports

# Run all modules
python -m cli.iraqaf_cli run-all --config configs/project.example.yaml --out reports

# Launch dashboard
streamlit run dashboard/app.py
```
Outputs are JSON files in `reports/` suitable for audit trails and paper appendices.
