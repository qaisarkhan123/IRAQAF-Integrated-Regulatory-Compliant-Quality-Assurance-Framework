from typing import Dict, Any
import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score
from ..common.utils import band_from_score

def _rate(y):
    # positive prediction rate
    return float(np.mean(y))

def evaluate(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    inputs:
      {
        "csv_path": "data/fairness_example.csv",
        "label_col": "y_true",
        "pred_col": "y_pred",   # or "y_prob" for probabilities
        "group_col": "group",
        "use_prob": false       # set true if pred_col is probabilities
      }
    """
    csv_path = inputs.get("csv_path")
    label_col = inputs.get("label_col", "y_true")
    pred_col  = inputs.get("pred_col", "y_pred")
    group_col = inputs.get("group_col", "group")
    use_prob  = bool(inputs.get("use_prob", False))

    df = pd.read_csv(csv_path)
    df = df[[label_col, pred_col, group_col]].dropna()

    # Overall AUROC (if probabilities available and both classes present)
    auroc = None
    if use_prob:
        y = df[label_col].values
        p = df[pred_col].values
        if len(np.unique(y)) > 1:
            try:
                auroc = float(roc_auc_score(y, p))
            except Exception:
                auroc = None

    # If using probabilities, binarize at 0.5 for parity metrics
    if use_prob:
        df["_yp"] = (df[pred_col].astype(float) >= 0.5).astype(int)
    else:
        df["_yp"] = df[pred_col].astype(int)

    # Demographic Parity Gap (max pairwise difference of positive rates)
    rates = df.groupby(group_col)["_yp"].apply(_rate).to_dict()
    if rates:
        rvals = list(rates.values())
        dpg = float(max(rvals) - min(rvals))
    else:
        dpg = 0.0

    # Equal Opportunity Difference (TPR gap)
    tprs = {}
    for g, sub in df.groupby(group_col):
        pos = sub[sub[label_col] == 1]
        if len(pos) == 0:
            tprs[g] = np.nan
        else:
            tprs[g] = float(np.mean(pos["_yp"]))
    # ignore groups with NaN TPR
    tvals = [v for v in tprs.values() if not np.isnan(v)]
    eod = float(max(tvals) - min(tvals)) if tvals else 0.0

    # Simple scoring: start from 100 and subtract scaled gaps
    # Targets: |DPG| <= 0.05, |EOD| <= 0.05
    score = 100.0
    score -= max(0.0, (dpg - 0.05)) * 400  # each +0.01 over 0.05 costs 4 points
    score -= max(0.0, (eod - 0.05)) * 400
    if auroc is not None:
        score = 0.8 * score + 0.2 * (auroc * 100.0)  # small reward for discrimination
    score = float(max(0.0, min(100.0, score)))

    metrics = {
        "DPG": round(dpg, 4),
        "EOD": round(eod, 4),
        "AUROC": round(auroc, 4) if auroc is not None else None,
        "rates_by_group": {str(k): round(float(v), 4) for k, v in rates.items()},
        "tpr_by_group": {str(k): (None if np.isnan(v) else round(float(v), 4)) for k, v in tprs.items()},
    }

    report = {
        "module": "L3",
        "version": "1.0",
        "metrics": metrics,
        "score": round(score, 2),
        "band": band_from_score(score, bands=(80, 95)),  # stricter bands for fairness
        "evidence": [csv_path],
        "notes": inputs.get("notes", ""),
    }
    return report
