#!/usr/bin/env python3
"""Leakage-aware train/validation/control-test/live-test splitter."""
import argparse, json, random
from collections import Counter, defaultdict
from pathlib import Path

def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--outdir", default="splits")
    ap.add_argument("--train", type=int, default=2000)
    ap.add_argument("--validation", type=int, default=400)
    ap.add_argument("--test-control", type=int, default=1000)
    ap.add_argument("--test-live", type=int, default=500)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--cutoff", default="")
    args = ap.parse_args()

    rows = load(args.input)
    random.Random(args.seed).shuffle(rows)

    live = [r for r in rows if r.get("source") == "livecodebench"]
    control = [r for r in rows if r.get("source") != "livecodebench"]

    def take(pool, n):
        return pool[:min(n, len(pool))], pool[min(n, len(pool)):]

    test_live, live_rest = take(live, args.test_live)
    test_control, control = take(control, args.test_control)
    train, control = take(control, args.train)
    validation, control = take(control, args.validation)

    assignments = [
        ("train", train),
        ("validation", validation),
        ("test_control", test_control),
        ("test_live", test_live)
    ]
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    for name, data in assignments:
        with open(outdir / f"{name}.jsonl", "w", encoding="utf-8") as g:
            for r in data:
                r["split"] = name
                if args.cutoff:
                    r.setdefault("contamination", {})["model_cutoff"] = args.cutoff
                    date = r.get("contamination", {}).get("release_date")
                    if date:
                        r["contamination"]["temporal_split"] = (
                            "post_cutoff" if str(date) > args.cutoff else "pre_cutoff"
                        )
                g.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("split sizes:")
    for name, data in assignments:
        print(f"  {name}: {len(data)}")

if __name__ == "__main__":
    main()
