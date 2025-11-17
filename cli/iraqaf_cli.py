
import argparse, yaml, json
from pathlib import Path
from iraqaf.modules.common.utils import save_report
from iraqaf.modules.l1_governance.evaluate import evaluate as eval_l1
from iraqaf.modules.l2_privsec.evaluate import evaluate as eval_l2
from iraqaf.modules.l3_fairness.evaluate import evaluate as eval_l3
from iraqaf.modules.l4_explain.evaluate import evaluate as eval_l4
from iraqaf.modules.l5_ops.evaluate import evaluate as eval_l5
from iraqaf.aggregate import aggregate

MODS = {"L1": eval_l1, "L2": eval_l2, "L3": eval_l3, "L4": eval_l4, "L5": eval_l5}

def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def run_module(mod, cfg, out):
    fn = MODS[mod]
    report = fn(cfg.get(mod, {}))
    path = save_report(report, out, mod)
    print(f"Saved {mod} report → {path}")
    return report

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("run")
    p1.add_argument("--module", required=True, choices=list(MODS.keys()))
    p1.add_argument("--config", required=True)
    p1.add_argument("--out", required=True)

    p2 = sub.add_parser("run-all")
    p2.add_argument("--config", required=True)
    p2.add_argument("--out", required=True)

    args = ap.parse_args()
    cfg = load_yaml(args.config)

    if args.cmd == "run":
        run_module(args.module, cfg, args.out)

    if args.cmd == "run-all":
        reports = {}
        for m in MODS.keys():
            reports[m] = run_module(m, cfg, args.out)
        agg = aggregate(reports["L1"], reports["L2"], reports["L3"], reports["L4"], reports["L5"])
        path = save_report(agg, args.out, "AGG")
        print(f"Saved AGG report → {path}")

if __name__ == "__main__":
    main()
