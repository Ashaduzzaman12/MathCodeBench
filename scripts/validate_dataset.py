#!/usr/bin/env python3
"""Validate unified MathCodeBench JSONL files and print dataset statistics."""
import argparse, json, sys
from collections import Counter
from pathlib import Path

REQUIRED = ["problem_id","source","title","statement","mathematics","programming","split"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    args = ap.parse_args()

    errors = []
    rows = []
    with open(args.input, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if not line.strip(): continue
            try:
                r = json.loads(line)
            except Exception as e:
                errors.append(f"line {i}: invalid JSON: {e}")
                continue
            rows.append(r)
            for k in REQUIRED:
                if k not in r:
                    errors.append(f"line {i}: missing {k}")
            m = r.get("mathematics", {})
            for k in ["math_complexity","reasoning_depth","proof_dependency","numerical_sensitivity"]:
                v = m.get(k)
                if v is not None and (not isinstance(v, int) or not 0 <= v <= 5):
                    errors.append(f"line {i}: {k} must be 0..5 or null")

    print(f"records={len(rows)}")
    print("sources:", dict(Counter(r.get("source") for r in rows)))
    print("splits:", dict(Counter(r.get("split") for r in rows)))
    print("math domains:", dict(Counter(
        r.get("mathematics",{}).get("primary_domain") for r in rows
    )))
    if errors:
        print(f"ERRORS={len(errors)}")
        for e in errors[:50]:
            print(" -", e)
        sys.exit(1)
    print("VALIDATION PASSED")

if __name__ == "__main__":
    main()
