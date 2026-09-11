#!/usr/bin/env python3
"""Extract CodeContests records from a practical JSON/JSONL(/gz) conversion.

The official DeepMind CodeContests release is Riegeli/protobuf. This script
expects a local JSON/JSONL conversion because it is much easier to process.
It preserves source metadata and reference solutions where available.
"""
import argparse, gzip, hashlib, json
from pathlib import Path

def open_text(path):
    path = Path(path)
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, "r", encoding="utf-8")

def stable_id(text):
    return "cc_" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

def normalize(raw):
    statement = raw.get("description") or raw.get("statement") or raw.get("question") or ""
    title = raw.get("name") or raw.get("title") or ""
    tests = raw.get("public_tests") or raw.get("tests") or []
    solutions = raw.get("solutions") or []

    # Support common CodeContests-extract shapes.
    public_tests = []
    if isinstance(tests, dict):
        inputs = tests.get("input", []) or []
        outputs = tests.get("output", []) or []
        for i, x in enumerate(inputs):
            public_tests.append({
                "input": x,
                "output": outputs[i] if i < len(outputs) else ""
            })
    elif isinstance(tests, list):
        for t in tests:
            if isinstance(t, dict):
                public_tests.append({
                    "input": t.get("input", ""),
                    "output": t.get("output", "")
                })

    source_meta = {
        "platform": raw.get("source") or raw.get("platform") or "CodeContests",
        "contest_id": raw.get("cf_contest_id"),
        "contest_index": raw.get("cf_index"),
        "rating": raw.get("cf_rating"),
        "tags": raw.get("cf_tags") or raw.get("tags") or []
    }

    if not isinstance(solutions, list):
        solutions = [solutions]

    refs = {"cpp": [], "python": [], "java": []}
    for s in solutions:
        if isinstance(s, str):
            refs["cpp"].append(s)
        elif isinstance(s, dict):
            code = s.get("code") or s.get("solution") or ""
            lang = (s.get("language") or "cpp").lower()
            if "python" in lang:
                refs["python"].append(code)
            elif "java" in lang:
                refs["java"].append(code)
            else:
                refs["cpp"].append(code)

    record = {
        "problem_id": stable_id(title + "\n" + statement),
        "source": "codecontests",
        "source_problem_id": str(raw.get("id") or raw.get("problem_id") or ""),
        "source_url": raw.get("source_url"),
        "title": title,
        "statement": statement,
        "input_specification": raw.get("input_specification", ""),
        "output_specification": raw.get("output_specification", ""),
        "constraints": raw.get("constraints", ""),
        "examples": raw.get("examples", []),
        "public_tests": public_tests,
        "private_tests_available": bool(raw.get("private_tests_available", True)),
        "reference_solutions": refs,
        "source_metadata": source_meta,
        "mathematics": {
            "primary_domain": None,
            "secondary_domains": [],
            "concepts": [],
            "math_complexity": None,
            "reasoning_depth": None,
            "proof_dependency": None,
            "numerical_sensitivity": None
        },
        "programming": {
            "algorithmic_complexity": None,
            "implementation_complexity": None,
            "estimated_time_complexity": None,
            "estimated_space_complexity": None
        },
        "difficulty": {
            "overall": None,
            "source_rating": source_meta["rating"]
        },
        "contamination": {
            "release_date": raw.get("contest_date") or raw.get("release_date"),
            "model_cutoff": None,
            "temporal_split": None,
            "duplicate_group_id": None,
            "near_duplicate": False
        },
        "split": None
    }
    return record

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Local JSON/JSONL or .gz file")
    ap.add_argument("--output", default="candidates/codecontests_candidates.jsonl")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with open_text(args.input) as f, open(out, "w", encoding="utf-8") as g:
        first = f.read(1)
        f.seek(0)
        if first == "[":
            data = json.load(f)
            iterator = data
        else:
            iterator = (json.loads(line) for line in f if line.strip())
        for raw in iterator:
            g.write(json.dumps(normalize(raw), ensure_ascii=False) + "\n")
            count += 1
            if args.limit and count >= args.limit:
                break
    print(f"wrote {count} records -> {out}")

if __name__ == "__main__":
    main()
