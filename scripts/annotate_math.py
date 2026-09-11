#!/usr/bin/env python3
"""Create annotation templates and optionally validate existing annotations.

Default mode creates a human-review JSONL template. No LLM API is required.
"""
import argparse, json
from pathlib import Path

DOMAINS = [
    "number_theory","combinatorics","probability","geometry","graph_theory",
    "dynamic_programming","optimization","linear_algebra","numerical_analysis","algebra","other"
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0

    with open(args.input, encoding="utf-8") as f, open(out, "w", encoding="utf-8") as g:
        for line in f:
            if not line.strip(): continue
            r = json.loads(line)
            m = r.setdefault("mathematics", {})
            if not args.validate:
                m["primary_domain"] = None
                m["secondary_domains"] = []
                m["concepts"] = []
                m["math_complexity"] = None
                m["reasoning_depth"] = None
                m["proof_dependency"] = None
                m["numerical_sensitivity"] = None
                r["_annotation_status"] = "needs_human_review"
            else:
                domain = m.get("primary_domain")
                vals = ["math_complexity","reasoning_depth","proof_dependency","numerical_sensitivity"]
                errors = []
                if domain not in DOMAINS:
                    errors.append("invalid primary_domain")
                for k in vals:
                    if not isinstance(m.get(k), int) or not 0 <= m[k] <= 5:
                        errors.append(f"{k} must be integer 0..5")
                r["_annotation_errors"] = errors
            g.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
    print(f"processed={n} -> {out}")

if __name__ == "__main__":
    main()
