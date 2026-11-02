#!/usr/bin/env python3
"""A small, human-reviewed evaluation harness for AI responses."""
import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

LABELS = {"pass", "fail", "uncertain"}

def read_cases(path):
    cases, seen = [], set()
    with open(path, encoding="utf-8") as f:
        for number, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                case = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {number}: invalid JSON: {exc.msg}") from exc
            if not isinstance(case, dict):
                raise ValueError(f"line {number}: expected an object")
            for key in ("id", "category", "prompt", "criterion"):
                if not isinstance(case.get(key), str) or not case[key].strip():
                    raise ValueError(f"line {number}: {key} must be a nonempty string")
            if case["id"] in seen:
                raise ValueError(f"line {number}: duplicate case id {case['id']!r}")
            seen.add(case["id"])
            cases.append(case)
    if not cases:
        raise ValueError("no cases found")
    return cases

def make_template(cases, output):
    with open(output, "x", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "category", "prompt", "criterion", "response", "verdict", "notes"])
        writer.writeheader()
        for case in cases:
            writer.writerow({key: case[key] for key in ("id", "category", "prompt", "criterion")})

def summarize(path):
    counts, categories, ids = Counter(), {}, set()
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"id", "category", "response", "verdict"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("CSV requires id, category, response and verdict columns")
        for number, row in enumerate(reader, 2):
            ident = (row.get("id") or "").strip()
            category = (row.get("category") or "").strip()
            if not ident or not category or ident in ids:
                raise ValueError(f"line {number}: missing or duplicate id, or missing category")
            ids.add(ident)
            label = (row.get("verdict") or "").strip().lower()
            if label and label not in LABELS:
                raise ValueError(f"line {number}: verdict must be pass, fail, uncertain, or blank")
            if label and not (row.get("response") or "").strip():
                raise ValueError(f"line {number}: a verdict requires a response")
            label = label or "unreviewed"
            counts[label] += 1
            categories.setdefault(category, Counter())[label] += 1
    if not ids:
        raise ValueError("no review rows found")
    print(f"Total: {len(ids)} | " + " | ".join(f"{k}: {counts[k]}" for k in ("pass", "fail", "uncertain", "unreviewed")))
    for category, c in sorted(categories.items()):
        print(f"  {category}: " + ", ".join(f"{k}={c[k]}" for k in ("pass", "fail", "uncertain", "unreviewed")))
    print("Human review only; these counts are not a safety certification.")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    new = sub.add_parser("template", help="Create a review CSV without calling a model")
    new.add_argument("cases", type=Path)
    new.add_argument("output", type=Path)
    s = sub.add_parser("summary", help="Summarise completed reviews")
    s.add_argument("reviews", type=Path)
    args = p.parse_args()
    try:
        if args.command == "template":
            make_template(read_cases(args.cases), args.output)
            print(f"Created {args.output}. Add model responses and human verdicts.")
        else:
            summarize(args.reviews)
    except (OSError, ValueError, csv.Error) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
