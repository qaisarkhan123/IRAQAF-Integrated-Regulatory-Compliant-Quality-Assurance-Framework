from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
import os
import json
import glob
import yaml
import hashlib

from ..common.utils import band_from_score

# ---------------------------
# Helpers
# ---------------------------


def _latest_reports(reports_dir: str) -> Dict[str, Dict[str, Any]]:
    latest: Dict[str, Tuple[float, Dict[str, Any]]] = {}
    for path in glob.glob(os.path.join(reports_dir, "*.json")):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            mod = data.get("module")
            if not mod:
                continue
            mtime = os.path.getmtime(path)
            prior = latest.get(mod)
            if (prior is None) or (mtime > prior[0]):
                latest[mod] = (mtime, data)
        except Exception:
            continue
    return {k: v[1] for k, v in latest.items()}


def _get_path(obj: Dict[str, Any], dotted: str) -> Optional[float]:
    parts = dotted.split(".")
    cur: Any = obj
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    try:
        return float(cur)
    except Exception:
        return None


def _module_score(obj: Dict[str, Any], module: str) -> Optional[float]:
    rep = obj.get(module)
    if not rep:
        return None
    try:
        return float(rep.get("score"))
    except Exception:
        return None


def _compare(val: Optional[float], rule: Dict[str, Any]) -> bool:
    if val is None:
        return False

    def has(k): return (k in rule) and (rule[k] is not None)
    if has("min") and not (val >= float(rule["min"])):
        return False
    if has("max") and not (val <= float(rule["max"])):
        return False
    if has("gt") and not (val > float(rule["gt"])):
        return False
    if has("gte") and not (val >= float(rule["gte"])):
        return False
    if has("lt") and not (val < float(rule["lt"])):
        return False
    if has("lte") and not (val <= float(rule["lte"])):
        return False
    return True


def _rule_pass_and_explain(latest_by_module: Dict[str, Any], rule: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
    # module score
    if "module" in rule and ("min_score" in rule or "max_score" in rule):
        mod = str(rule["module"])
        ms = _module_score(latest_by_module, mod)
        ok = _compare(ms, {"min": rule.get("min_score"),
                      "max": rule.get("max_score")})
        if ok:
            return True, None, None
        rng = []
        if rule.get("min_score") is not None:
            rng.append(f"≥ {rule['min_score']}")
        if rule.get("max_score") is not None:
            rng.append(f"≤ {rule['max_score']}")
        target = " & ".join(rng) if rng else "target"
        reason = f"{mod} score does not meet {target} (actual: {('missing' if ms is None else round(ms, 2))})"
        hint = f"Improve {mod} to meet {target}, or relax this clause for demos."
        return False, reason, hint

    # dotted metric
    if "metric" in rule:
        metric = str(rule["metric"])
        val = _get_path(latest_by_module, metric)
        ok = _compare(val, rule)
        if ok:
            return True, None, None
        targets = []
        for k in ("min", "max", "gt", "gte", "lt", "lte"):
            if rule.get(k) is not None:
                sym = {"min": "≥", "max": "≤", "gt": ">",
                       "gte": "≥", "lt": "<", "lte": "≤"}[k]
                targets.append(f"{sym} {rule[k]}")
        tgt = " & ".join(targets) if targets else "target range"
        reason = f"Metric {metric} not within bounds {tgt} (actual: {('missing' if val is None else round(val, 4))})"
        hint = f"Raise/lower the underlying metric or adjust the map for demos. Ensure the producing module emits '{metric}'."
        return False, reason, hint

    # exists / not_exists
    if "exists" in rule:
        mod = str(rule["exists"])
        ok = mod in latest_by_module
        if ok:
            return True, None, None
        return False, f"Evidence from {mod} not found", f"Run {mod} to produce a report in 'reports/'."

    if "not_exists" in rule:
        mod = str(rule["not_exists"])
        ok = mod not in latest_by_module
        if ok:
            return True, None, None
        return False, f"{mod} exists but clause required it to be absent", "Revisit mapping; 'not_exists' is rarely needed."

    return False, "Unrecognized rule schema", "Fix rule format in compliance_map.yaml"


def _evaluate_clause_with_explanation(latest_by_module: Dict[str, Any], clause: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
    if "all_of" in clause:
        for r in clause["all_of"]:
            ok, why, hint = _rule_pass_and_explain(latest_by_module, r)
            if not ok:
                return False, why, hint
        if "any_of" in clause:
            any_ok = False
            last_why, last_hint = None, None
            for r in clause["any_of"]:
                ok, why, hint = _rule_pass_and_explain(latest_by_module, r)
                if ok:
                    any_ok = True
                    break
                last_why, last_hint = why, hint
            if not any_ok:
                return False, last_why or "No rule in any_of satisfied", last_hint or "Satisfy at least one any_of rule."
        return True, None, None

    if "any_of" in clause:
        last_why, last_hint = None, None
        for r in clause["any_of"]:
            ok, why, hint = _rule_pass_and_explain(latest_by_module, r)
            if ok:
                return True, None, None
            last_why, last_hint = why, hint
        return False, last_why or "No rule in any_of satisfied", last_hint or "Satisfy at least one any_of rule."

    return False, "Clause has neither all_of nor any_of", "Define at least one rule."


def _load_evidence_index() -> Dict[str, list]:
    try:
        with open(os.path.join("configs", "evidence_index.json"), "r", encoding="utf-8") as fh:
            return json.load(fh) or {}
    except Exception:
        return {}


def _file_meta(path: str) -> Dict[str, Any]:
    try:
        st = os.stat(path)
        size = st.st_size
        with open(path, "rb") as fh:
            sha = hashlib.sha256(fh.read()).hexdigest()[:10]
        return {"exists": True, "size": size, "sha": sha}
    except Exception:
        return {"exists": False, "size": None, "sha": None}

# ---------------------------
# Main evaluate()
# ---------------------------


def evaluate(inputs: Dict[str, Any]) -> Dict[str, Any]:
    reports_dir = inputs.get("reports_dir", "reports")
    map_path = inputs.get("compliance_map", os.path.join(
        "configs", "compliance_map.yaml"))

    if not os.path.exists(map_path):
        raise FileNotFoundError(f"Compliance map not found: {map_path}")
    with open(map_path, "r", encoding="utf-8") as fh:
        kb = yaml.safe_load(fh) or {}

    latest_by_module = _latest_reports(reports_dir)
    frameworks: Dict[str, Any] = kb.get("frameworks", kb)

    # module-level evidence index (fallbacks)
    evidence_index = _load_evidence_index()

    clauses_out: List[Dict[str, Any]] = []
    per_framework: List[Dict[str, Any]] = []

    total_weight = 0.0
    total_earned = 0.0
    evidence_modules = sorted(latest_by_module.keys())

    for fw_name, fw_def in frameworks.items():
        clauses: List[Dict[str, Any]] = fw_def.get("clauses", [])
        fw_weight = 0.0
        fw_earned = 0.0
        fw_total_clauses = len(clauses)
        fw_covered_clauses = 0

        for cl in clauses:
            weight = float(cl.get("weight", 1.0))
            clause_id = cl.get("id")
            clause_desc = cl.get("description")

            passed, why_failed, hint = _evaluate_clause_with_explanation(
                latest_by_module, cl)

            fw_weight += weight
            total_weight += weight
            if passed:
                fw_earned += weight
                total_earned += weight
                fw_covered_clauses += 1

            # Clause-level evidence: explicit (from map) + module fallbacks (e.g., L1 docs)
            clause_evidence = list(cl.get("evidence", []) or [])
            # Example: if this clause references L1/L2 evidence via module keys
            # you can append defaults from evidence_index by module:
            # (Customize as needed)
            for mod_key in ("L1", "L2", "L3", "L4", "L5"):
                if mod_key in evidence_index:
                    # Only add as fallback when no explicit evidence provided
                    # (or keep both – here we keep both but de-dupe)
                    clause_evidence.extend(evidence_index.get(mod_key, []))
            # de-dupe while preserving order
            seen = set()
            clause_evidence = [p for p in clause_evidence if not (
                p in seen or seen.add(p))]

            # Augment evidence with quick file meta where possible
            ev_list = []
            for p in clause_evidence:
                meta = _file_meta(p) if isinstance(p, str) and not p.lower().startswith(
                    ("http://", "https://")) else {"exists": None, "size": None, "sha": None}
                ev_list.append({"path": p, **meta})

            clauses_out.append({
                "framework": fw_name,
                "id": clause_id,
                "description": clause_desc,
                "weight": float(weight),
                "passed": bool(passed),
                "why_failed": (None if passed else why_failed),
                "hint": (None if passed else hint),
                "logic": {"all_of": cl.get("all_of"), "any_of": cl.get("any_of")},
                "evidence_links": inputs.get("evidence", []),
            })

        coverage_pct = (fw_earned / fw_weight *
                        100.0) if fw_weight > 0 else 0.0
        per_framework.append({
            "framework": fw_name,
            "coverage_percent": round(coverage_pct, 2),
            "earned": fw_earned,
            "weight": fw_weight,
            "covered_clauses": int(fw_covered_clauses),
            "total_clauses": int(fw_total_clauses),
        })

    overall_pct = (total_earned / total_weight *
                   100.0) if total_weight > 0 else 0.0
    score = round(overall_pct, 2)
    band = band_from_score(score, bands=(80, 92))

    metrics = {
        "coverage_percent": round(overall_pct, 2),
        "framework_breakdown": per_framework,
        "clauses": clauses_out,
        "evidence_modules": evidence_modules
    }

    return {
        "module": "L1",
        "version": "1.0",
        "metrics": metrics,
        "score": score,
        "band": band,
        "evidence": [reports_dir, map_path],
        "notes": inputs.get("notes", "Compliance readiness computed from compliance_map.yaml and latest module reports."),
    }
