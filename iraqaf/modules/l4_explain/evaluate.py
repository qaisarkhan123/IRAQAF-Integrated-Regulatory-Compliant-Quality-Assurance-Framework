from typing import Dict, Any, List
import numpy as np
import pandas as pd

# optional SHAP (won't crash if missing)
try:
    import shap
    _HAS_SHAP = True
except Exception:
    _HAS_SHAP = False

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score
from sklearn.inspection import permutation_importance
from scipy.stats import kendalltau

from ..common.utils import band_from_score


def _infer_feature_cols_numeric(df: pd.DataFrame, label_col: str) -> List[str]:
    # only numeric columns, excluding label
    return [c for c in df.select_dtypes(include=[np.number]).columns if c != label_col]


def _metric_kind(y: np.ndarray) -> str:
    uniq = np.unique(y)
    return "auroc" if len(uniq) == 2 else "accuracy"


def _score_metric(kind: str, y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None) -> float:
    if kind == "auroc":
        if y_prob is not None and len(np.unique(y_true)) == 2:
            return float(roc_auc_score(y_true, y_prob))
        return float(accuracy_score(y_true, y_pred))
    return float(accuracy_score(y_true, y_pred))


def _rank_vector(importances: np.ndarray) -> np.ndarray:
    order = (-importances).argsort()
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(importances) + 1)
    return ranks


def evaluate(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inputs (YAML/JSON):
      csv_path: path to data file (required)
      label_col: name of label column (default: 'y')
      feature_cols: optional list of feature columns (default: infer numeric only)
      test_size: float, default 0.3
      random_state: int, default 42
      top_k: int for deletion test; default max(1, ceil(10% of features))
      metric: 'auroc' or 'accuracy' (auto-inferred if absent)
      notes: free text
    """
    csv_path = inputs.get("csv_path")
    if not csv_path:
        raise ValueError("L4 requires 'csv_path' in inputs")

    label_col = inputs.get("label_col", "y")
    test_size = float(inputs.get("test_size", 0.3))
    random_state = int(inputs.get("random_state", 42))

    # --- Load & basic cleaning
    df = pd.read_csv(csv_path)

    if label_col not in df.columns:
        raise ValueError(f"Label column '{label_col}' not found in {csv_path}")

    # Coerce label to numeric if possible
    df[label_col] = pd.to_numeric(df[label_col], errors="coerce")
    if df[label_col].isna().all():
        raise ValueError(
            f"Label column '{label_col}' could not be parsed as numeric in {csv_path}"
        )

    # Determine feature columns
    feature_cols = inputs.get("feature_cols")
    if feature_cols:
        # Keep order but coerce each to numeric
        for c in feature_cols:
            if c not in df.columns:
                raise ValueError(f"Feature '{c}' not found in {csv_path}")
            df[c] = pd.to_numeric(df[c], errors="coerce")
        # Drop features that became all-NaN after coercion
        keep = [c for c in feature_cols if not df[c].isna().all()]
        feature_cols = keep
    else:
        # Auto-infer numeric features only
        feature_cols = _infer_feature_cols_numeric(df, label_col)

    # Drop rows with any NaN in label or chosen features
    cols_needed = [label_col] + feature_cols
    df = df[cols_needed].dropna(axis=0, how="any")

    if len(feature_cols) == 0:
        raise ValueError(
            "No usable numeric feature columns found after coercion. "
            "Update config.feature_cols or clean your CSV to contain numeric features."
        )

    X = df[feature_cols].to_numpy(dtype=float, copy=False)
    y = df[label_col].to_numpy()

    # If binary but not 0/1, try to map unique values to 0/1
    uniq = np.unique(y[~np.isnan(y)])
    if len(uniq) == 2:
        # normalize to {0,1}
        y_bin = np.zeros_like(y, dtype=int)
        y_bin[df[label_col] == uniq[1]] = 1  # map larger/second to 1
        y = y_bin

    # train/test split
    strat = y if np.unique(y).size == 2 else None
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=strat
    )

    # simple, stable classifier
    clf = LogisticRegression(max_iter=1000, n_jobs=None)
    clf.fit(X_tr, y_tr)

    # baseline predictions
    y_prob = None
    if np.unique(y).size == 2 and hasattr(clf, "predict_proba"):
        y_prob = clf.predict_proba(X_te)[:, 1]
    y_pred = clf.predict(X_te)

    metric_kind = inputs.get("metric") or _metric_kind(y_te)
    baseline = _score_metric(metric_kind, y_te, y_pred, y_prob)

    # permutation importance on test split
    perm = permutation_importance(
        clf, X_te, y_te, n_repeats=8, random_state=random_state, n_jobs=None
    )
    importances = np.clip(perm.importances_mean, a_min=0.0,
                          a_max=None)  # negatives → 0
    ranks = _rank_vector(importances)

    # choose top-k for deletion test
    default_k = max(1, int(np.ceil(0.10 * X_te.shape[1])))
    top_k = int(inputs.get("top_k", default_k))
    top_idx = importances.argsort()[::-1][:top_k]

    # mask top-k features by setting them to training means
    train_means = X_tr.mean(axis=0)
    X_mask = X_te.copy()
    for j in top_idx:
        X_mask[:, j] = train_means[j]

    # re-score after deletion
    y_prob_mask = None
    if np.unique(y).size == 2 and hasattr(clf, "predict_proba"):
        y_prob_mask = clf.predict_proba(X_mask)[:, 1]
    y_pred_mask = clf.predict(X_mask)
    masked = _score_metric(metric_kind, y_te, y_pred_mask, y_prob_mask)

    deletion_drop = float(baseline - masked)

    # stability via bootstrap
    B = int(inputs.get("stability_bootstrap", 8))
    taus = []
    base_ranks = ranks
    rng = np.random.default_rng(random_state)
    n = X_te.shape[0]
    for _ in range(B):
        idx = rng.integers(0, n, size=n)
        perm_b = permutation_importance(
            clf, X_te[idx], y_te[idx], n_repeats=5, random_state=random_state
        )
        ranks_b = _rank_vector(
            np.clip(perm_b.importances_mean, a_min=0.0, a_max=None))
        tau, _ = kendalltau(base_ranks, ranks_b)
        if np.isfinite(tau):
            taus.append(float(tau))
    stability_tau = float(np.mean(taus)) if taus else 0.0

    # ---- Optional: SHAP importance (mean |SHAP|) + small sample for dashboard ----
    shap_importance = None
    shap_sample = None  # compact sample for beeswarm/waterfall
    if _HAS_SHAP:
        try:
            # For linear models this is fast & stable
            expl = shap.LinearExplainer(
                clf, X_tr, feature_perturbation="interventional")
            shap_vals = expl.shap_values(X_te)  # (n_samples, n_features)

            # expected_value may be scalar or array; normalize
            try:
                base_value = float(np.ravel(expl.expected_value)[0])
            except Exception:
                base_value = 0.0

            abs_mean = np.mean(np.abs(shap_vals), axis=0)
            shap_importance = {
                str(feature_cols[i]): float(abs_mean[i]) for i in range(len(feature_cols))
            }

            # Keep a small, deterministic sample for UI (so JSON doesn’t explode)
            max_rows = int(inputs.get("shap_sample_size", 300))
            rng = np.random.default_rng(int(inputs.get("random_state", 42)))
            if X_te.shape[0] > 0:
                take = min(max_rows, X_te.shape[0])
                idx = rng.choice(X_te.shape[0], size=take, replace=False)
                shap_sample = {
                    "feature_names": [str(c) for c in feature_cols],
                    "values": shap_vals[idx, :].tolist(),   # list[list[float]]
                    "base_value": float(base_value),
                    "indices": idx.tolist(),
                }
        except Exception:
            shap_importance = None
            shap_sample = None

    # derive "infidelity" proxy (lower is better). Target: deletion_drop >= 0.15
    target_drop = 0.15
    shortfall = max(0.0, target_drop - deletion_drop)
    infidelity = float(min(1.0, shortfall / target_drop))

    # Scoring
    score = 100.0
    score -= (shortfall * 400.0)                 # deletion gap
    target_tau = 0.85
    tau_deficit = max(0.0, target_tau - stability_tau)
    score -= (tau_deficit * 400.0)               # stability gap
    score = float(max(0.0, min(100.0, score)))
    # Red<75, Yellow 75–89, Green>=90
    band = band_from_score(score, bands=(75, 90))

    metrics = {
        "baseline_metric": round(baseline, 4),
        "masked_metric": round(masked, 4),
        "deletion_drop": round(deletion_drop, 4),
        "stability_tau": round(stability_tau, 4),
        "infidelity": round(infidelity, 4),
        "top_k": int(top_k),
        "feature_importance": {
            str(feature_cols[i]): float(importances[i]) for i in range(len(feature_cols))
        },
        "shap_importance": shap_importance,  # may be None
        # compact SHAP values for UI (may be None)
        "shap_sample": shap_sample,
    }

    return {
        "module": "L4",
        "version": "1.0",
        "metrics": metrics,
        "score": round(score, 2),
        "band": band,
        "evidence": [csv_path],
        "notes": inputs.get("notes", "Permutation-importance deletion test + bootstrap stability"),
    }
