# dashboard/helpers.py
from __future__ import annotations

import glob
import hashlib
import io
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Tuple, Union, Dict, Any

import pandas as pd
import altair as alt
import streamlit as st

# yaml is optional; expose both yaml and _yaml when available
try:
    import yaml  # type: ignore
    _yaml = yaml
except Exception:  # pragma: no cover
    yaml = None
    _yaml = None


# =========================
# ⚡ PERFORMANCE & CACHING
# =========================

@st.cache_data(show_spinner=False, ttl=60)
def _load_json(path: str) -> Optional[dict]:
    """(LEGACY) Cached JSON loader. Returns None on failure."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


@st.cache_data(show_spinner=False, ttl=60)
def _load_csv(path_or_buffer: Union[str, os.PathLike, io.BytesIO]) -> pd.DataFrame:
    """(LEGACY) Cached CSV reader (file path or upload buffer)."""
    return pd.read_csv(path_or_buffer)


@st.cache_resource(show_spinner=False)
def _cached_fit(file_bytes: bytes):
    """
    (LEGACY) Cache heavy model-fit calls by file content.
    If your app defines _fit_and_measure_from_bytes() it will be used.
    """
    try:
        # Imported dynamically if present in app; harmless if not.
        from dashboard.app import _fit_and_measure_from_bytes  # type: ignore
        return _fit_and_measure_from_bytes(file_bytes)
    except Exception:
        # Fallback: return bytes so caller can decide/ignore
        return file_bytes


# User-friendly aliases (optional)
load_json = _load_json
load_csv = _load_csv
cached_fit = _cached_fit


# ===============================
# 📎 CLAUSE / EVIDENCE UTILITIES
# ===============================

def _normalize_clause_evidence(l1_report: dict) -> dict:
    """(LEGACY) Ensure every L1 clause has an 'evidence_links' list."""
    if not l1_report:
        return {}
    metrics = l1_report.get("metrics", {}) or {}
    clauses = metrics.get("clauses") or []
    module_ev = l1_report.get("evidence") or []
    fixed = []
    for c in clauses:
        ev_links: List[str] = []
        if isinstance(c.get("evidence_links"), list):
            ev_links.extend([str(x) for x in c["evidence_links"]])
        elif isinstance(c.get("evidence"), list):
            for item in c["evidence"]:
                if isinstance(item, dict) and "path" in item:
                    ev_links.append(str(item["path"]))
                elif isinstance(item, str):
                    ev_links.append(item)
        if not ev_links and module_ev:
            for item in module_ev:
                ev_links.append(item if isinstance(item, str) else str(item))
        c["evidence_links"] = sorted({str(p) for p in ev_links})
        fixed.append(c)
    metrics["clauses"] = fixed
    l1_report["metrics"] = metrics
    return l1_report


def _evidence_count(module_id: str) -> int:
    """(LEGACY) Count pinned evidence for a module from configs/evidence_index.json."""
    idx_path = Path("configs/evidence_index.json")
    if not idx_path.exists():
        return 0
    try:
        data = json.loads(idx_path.read_text(encoding="utf-8")) or {}
        return len(data.get(module_id, []))
    except Exception:
        return 0


# Optional aliases
normalize_clause_evidence = _normalize_clause_evidence
evidence_count = _evidence_count


# ========================
# 🧭 REPORT PATH HELPERS
# ========================

def _label_from_path(p: str) -> str:
    """(LEGACY) Friendly label from report path (prefers embedded timestamp)."""
    base = os.path.basename(p).replace(".json", "")
    m = re.search(r"(\d{8}-\d{6})", base)
    return m.group(1) if m else base


def _file_mtime_seconds(path: str) -> float | None:
    """Return file mtime as a Unix timestamp (seconds), or None if not available."""
    try:
        return os.path.getmtime(path)
    except Exception:
        return None


def _parse_timestamp_from_name(path: str) -> float | None:
    """
    Best-effort: pull a timestamp out of a filename like
    '...2024-05-31...', '...20240531...', or '...20240531_142355...'
    Returns Unix timestamp seconds or None.
    """
    name = os.path.basename(path)
    m = re.search(
        r'(\d{4})[-_]?(\d{2})[-_]?(\d{2})(?:[ T_-]?(\d{2})(\d{2})(\d{2}))?',
        name,
    )
    if not m:
        return None
    y, mo, d, hh, mm, ss = m.groups()
    hh = int(hh) if hh else 0
    mm = int(mm) if mm else 0
    ss = int(ss) if ss else 0
    try:
        dt = datetime(int(y), int(mo), int(d), hh, mm, ss)
        return dt.timestamp()
    except Exception:
        return None


def _best_timestamp(path: str) -> float | None:
    """Prefer filesystem mtime; fall back to a date parsed from the filename."""
    ts = _file_mtime_seconds(path)
    if ts is not None:
        return ts
    return _parse_timestamp_from_name(path)


def _nearest_by_time(
    candidates: List[str],
    reference: str | float | int | datetime,
) -> Optional[str]:
    """
    Pick the candidate file whose timestamp is closest to the reference.

    - candidates: list of file paths
    - reference: a path (str), a Unix timestamp (float/int), or a datetime
    Returns the chosen path or None if nothing usable.

    NOTE: This is backward-compatible with older calls like
          _nearest_by_time(l1_paths, agg_paths[0]) where the reference is a path.
    """
    # Resolve reference timestamp
    if isinstance(reference, datetime):
        ref_ts: Optional[float] = reference.timestamp()
    elif isinstance(reference, (int, float)):
        ref_ts = float(reference)
    elif isinstance(reference, str):
        ref_ts = _best_timestamp(reference)
    else:
        ref_ts = None

    if ref_ts is None:
        return None

    best_path: Optional[str] = None
    best_delta: Optional[float] = None

    for p in candidates or []:
        ts = _best_timestamp(p)
        if ts is None:
            continue
        delta = abs(ts - ref_ts)
        if best_delta is None or delta < best_delta:
            best_delta = delta
            best_path = p

    return best_path


def _current_agg_path(reports_dir: str = "reports") -> Optional[str]:
    """(LEGACY) Newest AGG-*.json path; does NOT rely on a global `files` list."""
    try:
        agg_paths = [
            p for p in glob.glob(os.path.join(reports_dir, "*.json"))
            if os.path.basename(p).startswith("AGG-")
        ]
        if not agg_paths:
            return None
        return max(agg_paths, key=os.path.getmtime)
    except Exception:
        return None


def _audit_snapshot_hash(report_paths: Iterable[str]) -> str:
    """(LEGACY) Short SHA256 of concatenated report files (content-based)."""
    h = hashlib.sha256()
    for p in sorted(report_paths):
        try:
            with open(p, "rb") as fh:
                h.update(fh.read())
        except Exception:
            pass
    return h.hexdigest()[:16]


@st.cache_data(show_spinner=False, ttl=300)
def _hash_file(path: str, _mtime: float = None) -> Optional[str]:
    """
    Full SHA256 of a file; None on error.
    _mtime exists solely for cache invalidation; it is not used.
    """
    try:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except FileNotFoundError:
        # the tests expect a warning log line in app; helpers stay quiet
        return None
    except PermissionError:
        return None
    except Exception:
        return None


# Optional aliases
label_from_path = _label_from_path
nearest_by_time = _nearest_by_time
current_agg_path = _current_agg_path
audit_snapshot_hash = _audit_snapshot_hash
sha256_file = _hash_file


# ===============================
# 🎨 UI / TEXT / NUMBER HELPERS
# ===============================

def _delta_badge(new: Optional[float], old: Optional[float]) -> str:
    """(LEGACY) HTML badge for deltas: ▲/▼/■ with color."""
    if new is None or old is None:
        return "—"
    d = float(new) - float(old)
    arrow = "▲" if d > 0 else ("▼" if d < 0 else "■")
    color = "#00c851" if d > 0 else ("#ff4b4b" if d < 0 else "#999999")
    return f"<span style='color:{color}'>{arrow} {d:+.2f}</span>"


def _human_size(n: int) -> str:
    """(LEGACY) Format bytes into human-readable units."""
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.0f} TB"


def _sanitize_name(name: str) -> str:
    """
    (LEGACY) Sanitize a display/name into a safe value:
    - replace path separators with underscores
    - strip characters not in [A-Za-z0-9-_.() and space]
    - collapse whitespace
    """
    if name is None:
        return ""
    s = str(name)
    s = s.replace("\\", "_").replace("/", "_")
    s = re.sub(r"[^A-Za-z0-9\-\._\(\) ]+", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# Optional aliases
delta_badge = _delta_badge
human_size = _human_size
sanitize_name = _sanitize_name


# ================================
# 👀 INLINE FILE PREVIEW WIDGET
# ================================

def _preview_widget(fp: Path):
    """(LEGACY) Inline preview for common file types. Fail-safe."""
    if not fp.exists():
        st.warning("File not found on disk.")
        return
    suffix = fp.suffix.lower()
    try:
        # Tabular
        if suffix == ".csv":
            st.dataframe(pd.read_csv(fp), width="stretch")
        elif suffix == ".tsv":
            st.dataframe(pd.read_csv(fp, sep="\t"), width="stretch")
        elif suffix in [".xlsx", ".xls"]:
            try:
                st.dataframe(pd.read_excel(fp), width="stretch")
            except Exception as e:
                st.error(f"Excel preview error: {e}")
        # Structured text
        elif suffix == ".json":
            st.json(json.loads(fp.read_text(encoding="utf-8")))
        elif suffix in [".yaml", ".yml"]:
            text = fp.read_text(encoding="utf-8")
            st.code(text, language="yaml")
            if _yaml:
                try:
                    parsed = _yaml.safe_load(text)
                    if parsed is not None:
                        st.caption("Parsed YAML")
                        st.json(parsed)
                except Exception as e:
                    st.info(f"YAML parse note: {e}")
        # Plain/code
        elif suffix in [".txt", ".log", ".md", ".py"]:
            text = fp.read_text(encoding="utf-8", errors="ignore")
            st.code(text[:20000])
        # Images
        elif suffix in [".png", ".jpg", ".jpeg", ".gif", ".bmp"]:
            try:
                from PIL import Image
                st.image(Image.open(fp), caption=fp.name, width="stretch")
            except Exception:
                st.image(str(fp), caption=fp.name, width="stretch")
        # PDFs & others
        elif suffix == ".pdf":
            st.info("PDF inline preview is limited. Use the Download button.")
        else:
            st.info("No inline preview for this file type. Use the Download button.")
    except Exception as e:
        st.error(f"Preview error: {e}")


# Optional alias
preview_widget = _preview_widget


# ========================================
# 📈 Uncertainty Bands (Altair ribbon)
# ========================================

def ribbon_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    lo_col: str,
    hi_col: str,
    title: str,
    y_domain: Optional[Tuple[float, float]] = None,
) -> alt.Chart:
    """
    Plot a line with a shaded uncertainty ribbon, when df contains y_lo/y_hi.
    """
    band = alt.Chart(df).mark_area(opacity=0.15).encode(
        x=alt.X(f"{x_col}:Q", title="Run #"),
        y=alt.Y(
            f"{lo_col}:Q",
            title=title,
            scale=alt.Scale(domain=y_domain) if y_domain else alt.Undefined,
        ),
        y2=f"{hi_col}:Q",
        tooltip=[x_col, lo_col, hi_col],
    )
    line = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X(f"{x_col}:Q"),
        y=alt.Y(
            f"{y_col}:Q",
            title=title,
            scale=alt.Scale(domain=y_domain) if y_domain else alt.Undefined,
        ),
        tooltip=[x_col, y_col],
    )
    return band + line
