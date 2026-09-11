#!/usr/bin/env python3
"""High-recall mathematical-programming candidate detector."""
import argparse, json, re
from pathlib import Path

KEYWORDS = {
    "number_theory": ["prime", "divisor", "gcd", "lcm", "modulo", "modular", "factor", "diophantine", "sieve", "congruence"],
    "combinatorics": ["permutation", "combination", "binomial", "count the number", "combinatorial", "inclusion-exclusion", "catalan"],
    "probability": ["probability", "expected value", "expectation", "random", "distribution", "variance", "bayes"],
    "geometry": ["geometry", "point", "vector", "cross product", "dot product", "polygon", "circle", "convex hull", "angle", "coordinate"],
    "graph_theory": ["graph", "tree", "shortest path", "dijkstra", "topological", "matching", "flow", "bipartite", "spanning tree"],
    "dynamic_programming": ["dynamic programming", "dp", "recurrence", "memoization", "state transition"],
    "optimization": ["optimize", "minimum cost", "maximum value", "minimize", "maximize", "linear programming", "convex"],
    "linear_algebra": ["matrix", "determinant", "eigenvalue", "eigenvector", "linear algebra", "matrix multiplication"],
    "numerical_analysis": ["numerical", "precision", "floating point", "epsilon", "convergence", "integration", "interpolation", "root finding"],
    "algebra": ["polynomial", "equation", "inequality", "logarithm", "exponent", "algebraic"]
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--threshold", type=int, default=1)
    args = ap.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    kept = 0
    total = 0

    with open(args.input, encoding="utf-8") as f, open(out, "w", encoding="utf-8") as g:
        for line in f:
            if not line.strip(): continue
            total += 1
            r = json.loads(line)
            text = " ".join([
                r.get("title",""), r.get("statement",""), r.get("constraints",""),
                r.get("input_specification",""), r.get("output_specification","")
            ]).lower()
            hits = {}
            for domain, words in KEYWORDS.items():
                n = sum(len(re.findall(r"\b" + re.escape(w) + r"\b", text)) for w in words)
                if n:
                    hits[domain] = n
            score = sum(hits.values())
            if score >= args.threshold:
                r["_math_detection"] = {
                    "score": score,
                    "domains": sorted(hits, key=hits.get, reverse=True),
                    "keyword_hits": hits
                }
                g.write(json.dumps(r, ensure_ascii=False) + "\n")
                kept += 1
    print(f"scanned={total} kept={kept} -> {out}")

if __name__ == "__main__":
    main()
