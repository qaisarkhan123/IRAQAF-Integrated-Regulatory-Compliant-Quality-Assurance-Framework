from datetime import datetime
import hashlib
import os
import streamlit as st

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
AUDIT_LOG = os.path.join(LOG_DIR, "audit.log")


def hash_file(path: str) -> str | None:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def record_audit_event(action: str, run_hash: str | None = None):
    """Append an immutable line to logs/audit.log."""
    t = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{t}\t{action}\t{run_hash or 'n/a'}\n"
    try:
        with open(AUDIT_LOG, "a", encoding="utf-8") as fh:
            fh.write(line)
    except Exception:
        pass


def audit_locked() -> bool:
    """Shortcut for checking audit lock state."""
    return bool(st.session_state.get("__audit_mode__", False))
