#!/usr/bin/env python3
"""OpenRouter Images -- CSV Batch Workflow

Parse a CSV file of image generation requests and output a structured plan.

Usage:
    batch.py --csv path/to/file.csv

CSV columns:
    prompt (required), ratio, resolution, model (all optional)

Example CSV:
    prompt,ratio,resolution,model
    "coffee shop hero image",16:9,2K,google/gemini-3.1-flash-image-preview
    "team photo placeholder",1:1,1K,google/gemini-2.5-flash-image
    "product shot on marble",4:3,2K,google/gemini-3.1-flash-image-preview
"""

import argparse
import csv
import json
import sys
from pathlib import Path

PRICING = {
    "google/gemini-3.1-flash-image-preview": {"1K": 0.04, "2K": 0.08, "4K": 0.16},
    "google/gemini-2.5-flash-image": {"1K": 0.03, "2K": 0.06, "4K": 0.12},
    "bytedance-seed/seedream-4.5": {"1K": 0.04, "2K": 0.04},
    "sourceful/riverflow-v2-fast": {"1K": 0.02, "2K": 0.04},
    "sourceful/riverflow-v2-pro": {"1K": 0.15, "2K": 0.15, "4K": 0.33},
    "openai/gpt-5-image-mini": {"1K": 0.02, "2K": 0.02},
}
DEFAULT_MODEL = "google/gemini-3.1-flash-image-preview"
DEFAULT_RESOLUTION = "1K"
DEFAULT_RATIO = "1:1"


def estimate_cost(model, resolution):
    model_pricing = PRICING.get(model, PRICING[DEFAULT_MODEL])
    return model_pricing.get(resolution, model_pricing.get("1K", 0.04))


def main():
    parser = argparse.ArgumentParser(description="Parse CSV batch and output generation plan")
    parser.add_argument("--csv", required=True, help="Path to CSV file")
    args = parser.parse_args()

    csv_path = Path(args.csv).resolve()
    if not csv_path.exists():
        print(json.dumps({"error": True, "message": f"CSV not found: {csv_path}"}))
        sys.exit(1)

    rows = []
    errors = []

    try:
        with open(csv_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or "prompt" not in reader.fieldnames:
                print(json.dumps({"error": True, "message": "CSV must have a 'prompt' column header"}))
                sys.exit(1)
            for i, row in enumerate(reader, start=2):
                prompt = row.get("prompt", "").strip()
                if not prompt:
                    errors.append(f"Row {i}: missing prompt")
                    continue
                rows.append({
                    "row": i,
                    "prompt": prompt,
                    "ratio": row.get("ratio", "").strip() or DEFAULT_RATIO,
                    "resolution": row.get("resolution", "").strip() or DEFAULT_RESOLUTION,
                    "model": row.get("model", "").strip() or DEFAULT_MODEL,
                })
    except (csv.Error, UnicodeDecodeError) as e:
        print(json.dumps({"error": True, "message": f"Failed to parse CSV: {e}"}))
        sys.exit(1)

    if errors:
        print("Validation errors:")
        for e in errors:
            print(f"  - {e}")
        if not rows:
            sys.exit(1)
        print()

    total_cost = sum(estimate_cost(r["model"], r["resolution"]) for r in rows)
    print(json.dumps({"rows": rows, "total_count": len(rows), "estimated_cost": round(total_cost, 3), "errors": errors}, indent=2))


if __name__ == "__main__":
    main()
