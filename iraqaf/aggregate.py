
from typing import Dict
def aggregate(crs: Dict, sai: Dict, fi: Dict, ts: Dict, ops: Dict):
    weights = {"CRS": 0.30, "SAI": 0.25, "FI": 0.20, "TS": 0.15, "OPS": 0.10}
    score = (weights["CRS"]*crs["score"] + weights["SAI"]*sai["score"] +
             weights["FI"]*fi["score"] + weights["TS"]*ts["score"] +
             weights["OPS"]*ops["score"])
    return {
        "module": "AGG",
        "version": "0.1",
        "scores": {"CRS": crs["score"], "SAI": sai["score"], "FI": fi["score"], "TS": ts["score"], "OPS": ops["score"]},
        "gqas": round(score, 2),
        "floors_met": all([
            crs["score"] >= 90, sai["score"] >= 90, fi["score"] >= 95, ts["score"] >= 90, ops["score"] >= 85
        ])
    }
