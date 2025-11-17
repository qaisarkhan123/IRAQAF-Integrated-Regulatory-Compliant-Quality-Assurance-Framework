
from dataclasses import dataclass
from typing import Dict, Any
import json
import hashlib
from pathlib import Path
import time

def save_report(obj: Dict[str, Any], out_dir: str, name: str):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    path = Path(out_dir) / f"{name}-{ts}.json"
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
    return str(path)

def band_from_score(score: float, bands=(70, 90)):
    if score < bands[0]:
        return "red"
    if score < bands[1]:
        return "yellow"
    return "green"

def hash_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()
