#!/usr/bin/env python3
"""Extract LiveCodeBench code-generation problems into the unified schema."""
import argparse, hashlib, json
from pathlib import Path

def stable_id(text):
    return "lcb_" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="candidates/livecodebench_candidates.jsonl")
    ap.add_argument("--release", default="release_v6")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    try:
        from datasets import load_dataset
    except ImportError:
        raise SystemExit("Install datasets first: pip install datasets")

    ds = load_dataset("livecodebench/code_generation_lite", args.release, split="test")
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    n = 0
    with open(out, "w", encoding="utf-8") as g:
        for row in ds:
            title = row.get("question_title", "")
            statement = row.get("question_content", "")
            tests = row.get("public_test_cases") or []
            private = row.get("private_test_cases") or []

            def parse_tests(xs):
                result = []
                for t in xs:
                    if isinstance(t, dict):
                        result.append({
                            "input": t.get("input", ""),
                            "output": t.get("output", "")
                        })
                    elif isinstance(t, str):
                        result.append({"input": t, "output": ""})
                return result

            record = {
                "problem_id": stable_id(title + "\n" + statement),
                "source": "livecodebench",
                "source_problem_id": str(row.get("question_id") or ""),
                "source_url": row.get("question_url"),
                "title": title,
                "statement": statement,
                "input_specification": "",
                "output_specification": "",
                "constraints": "",
                "examples": [],
                "public_tests": parse_tests(tests),
                "private_tests_available": bool(private),
                "reference_solutions": {"cpp": [], "python": [], "java": []},
                "source_metadata": {
                    "platform": row.get("platform"),
                    "contest_id": row.get("contest_id"),
                    "contest_index": None,
                    "rating": row.get("difficulty"),
                    "tags": (row.get("metadata") or {}).get("tags", [])
                        if isinstance(row.get("metadata"), dict) else []
                },
                "mathematics": {
                    "primary_domain": None, "secondary_domains": [], "concepts": [],
                    "math_complexity": None, "reasoning_depth": None,
                    "proof_dependency": None, "numerical_sensitivity": None
                },
                "programming": {
                    "algorithmic_complexity": None, "implementation_complexity": None,
                    "estimated_time_complexity": None, "estimated_space_complexity": None
                },
                "difficulty": {
                    "overall": row.get("difficulty"),
                    "source_rating": row.get("difficulty")
                },
                "contamination": {
                    "release_date": row.get("contest_date"),
                    "model_cutoff": None, "temporal_split": None,
                    "duplicate_group_id": None, "near_duplicate": False
                },
                "split": None
            }
            g.write(json.dumps(record, ensure_ascii=False) + "\n")
            n += 1
            if args.limit and n >= args.limit:
                break
    print(f"wrote {n} records -> {out}")

if __name__ == "__main__":
    main()
