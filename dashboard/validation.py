from __future__ import annotations
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from datetime import datetime
import json
import yaml

SCHEMA_VERSION = "1.0.0"

# -----------------------------
#  Core Models
# -----------------------------


class Clause(BaseModel):
    id: str
    framework: str
    passed: Optional[bool]
    why_failed: Optional[str] = None
    hint: Optional[str] = None
    evidence_links: Optional[List[str]] = []
    evidence: Optional[List[str]] = []


class Metrics(BaseModel):
    clauses: Optional[List[Clause]] = []
    summary: Optional[Dict[str, float]] = {}


class ReportFile(BaseModel):
    schema_version: str = Field(default=SCHEMA_VERSION)
    module: str
    score: Optional[float]
    band: Optional[str]
    metrics: Optional[Metrics] = None
    timestamp: Optional[datetime] = None

    @validator("module")
    def valid_module(cls, v):
        if v not in {"L1", "L2", "L3", "L4", "L5", "AGG"}:
            raise ValueError(f"Invalid module '{v}'")
        return v


class Incident(BaseModel):
    time: datetime
    kind: str
    severity: str
    latency_s: Optional[float]
    error_rate_pct: Optional[float]
    note: Optional[str]


class TraceLink(BaseModel):
    clause: str
    metric: str

# -----------------------------
#  Helpers
# -----------------------------


def validate_report(path: str) -> ReportFile | None:
    """Load & validate any IRAQAF JSON report"""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        rpt = ReportFile(**raw)
        if rpt.schema_version != SCHEMA_VERSION:
            migrate_schema(raw, rpt.schema_version)
        return rpt
    except Exception as e:
        import traceback
        tb = "".join(traceback.format_exception_only(type(e), e))
        import streamlit as st
        st.error(f"⚠️ Validation failed for {path}: {tb}")
        return None


def validate_incidents(path: str) -> list[Incident]:
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return [Incident(**r) for r in raw]


def validate_trace_map(path: str) -> list[TraceLink]:
    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    return [TraceLink(**r) for r in raw.get("links", [])]


def migrate_schema(raw: dict, old_ver: str):
    """Very simple migrator stub"""
    # Example: add missing keys
    if "schema_version" not in raw:
        raw["schema_version"] = SCHEMA_VERSION
    # TODO: add real field migrations when version bumps
    return raw
