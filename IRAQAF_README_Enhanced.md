# 🧠 IRAQAF Starter Kit — Enhanced Demo Version (Updated 2025-11-07)

## 🎯 Overview
Streamlit-based AI Assurance Dashboard implementing **IRAQAF** (L1–L5) for demo and pre-integration validation.

## ⚙️ Run
```bat
python -m cli.iraqaf_cli run-all --config configs\project.example.yaml --out reports
python -m cli.iraqaf_cli run --module L4 --config configs\project.example.yaml --out reports
streamlit run dashboard\app.py
```
Reports: `reports/Lx-YYYYMMDD-HHMMSS.json`

## 📊 Dashboard Features (added today)
- Risk profile toggle (High/Medium)
- Strict ↔ Lenient compliance maps + active map indicator
- Module Summary with evidence counts
- Evidence Tray with search, expand-all, preview-all (CSV/JSON/YAML/Text/Image/PDF)
- L1: Framework coverage chart + Clause drill-through (two-run compare, flips, hints)
- L3: DPG/EOD/AUROC trends + latest group diagnostics
- L4: Interactive health gauge, SHAP/Permutation toggle, Top‑N, trends
- L5: Ops trends (logging_coverage, alert_latency_h)
- AGG: Compare runs & GQAS trend
- Export: JSON/CSV + Word report

## 📁 Structure
```
configs/
  project.example.yaml
  compliance_map.strict.yaml
  compliance_map.lenient.yaml
  compliance_map.yaml
  evidence_index.json
dashboard/app.py
iraqaf/modules/l1_governance/evaluate.py
iraqaf/modules/l4_explain/evaluate.py
reports/
use_lenient_map.bat
use_strict_map.bat
```

## 🧰 Map Switchers
```
use_lenient_map.bat  → copies configs\compliance_map.lenient.yaml → configs\compliance_map.yaml
use_strict_map.bat   → copies configs\compliance_map.strict.yaml  → configs\compliance_map.yaml
```

## 📈 Demo Targets
L4: deletion_drop ≥ 0.15, stability_tau ≥ 0.85 (or relax temp in evaluator).  
L1: lenient map and fallback evidence rules; set Risk=Medium for presentations.

## 📎 Evidence Index
Create once:
```bat
cd configs
python -c "import json; data={'L1':['docs/intended_use.pdf','docs/pms_plan.pdf'],'L2':['configs/security.yaml'],'L3':['data/fairness_example.csv'],'L4':['data/explain_demo.csv'],'L5':['logs/telemetry.csv']}; json.dump(data, open('evidence_index.json','w'), indent=2)"
```

## 🪄 TL;DR
Generate reports with CLI, switch maps with BATs, and present everything in Streamlit.
