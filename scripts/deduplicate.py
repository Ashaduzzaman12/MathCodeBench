#!/usr/bin/env python3
"""Exact and approximate text deduplication for JSONL problems."""
import argparse, hashlib, json, re
from pathlib import Path
from difflib import SequenceMatcher

def norm(s):
    s = (s or "").lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return s.strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--threshold", type=float, default=0.90)
    args = ap.parse_args()

    records = []
    with open(args.input, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    seen = {}
    exact = []
    unique = []

    for r in records:
        text = norm(r.get("title","") + "\n" + r.get("statement",""))
        h = hashlib.sha256(text.encode()).hexdigest()
        if h in seen:
            exact.append({"problem_id": r.get("problem_id"), "duplicate_of": seen[h]})
            continue
        seen[h] = r.get("problem_id")
        r.setdefault("contamination", {})["duplicate_group_id"] = h[:16]
        unique.append(r)

    # O(n^2) approximate pass. Good for small/medium candidate sets.
    # For large corpora, replace with MinHash/FAISS/embedding clustering.
    kept = []
    near = []
    signatures = []
    for r in unique:
        text = norm(r.get("title","") + "\n" + r.get("statement",""))
        duplicate = False
        for old_id, old_text in signatures:
            ratio = SequenceMatcher(None, text, old_text).ratio()
            if ratio >= args.threshold:
                r.setdefault("contamination", {})["near_duplicate"] = True
                near.append({"problem_id": r.get("problem_id"), "duplicate_of": old_id, "ratio": ratio})
                duplicate = True
                break
        if not duplicate:
            kept.append(r)
            signatures.append((r.get("problem_id"), text))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as g:
        for r in kept:
            g.write(json.dumps(r, ensure_ascii=False) + "\n")

    report = out.parent.parent / "dedup" / "dedup_report.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps({
        "input": len(records),
        "exact_duplicates": exact,
        "near_duplicates": near,
        "kept": len(kept)
    }, indent=2), encoding="utf-8")

    print(f"input={len(records)} exact={len(exact)} near={len(near)} kept={len(kept)}")
    print(f"report -> {report}")

if __name__ == "__main__":
    main()
