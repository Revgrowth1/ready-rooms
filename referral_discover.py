#!/usr/bin/env python3
"""
Ready Rooms - Referral Source Discovery Pipeline

Discovers organizations and contacts that can refer or fund housing
placements for target populations.

Usage:
    python referral_discover.py houston          # Run full pipeline
    python referral_discover.py houston --step 3  # Run specific step
    python referral_discover.py houston --from 3   # Resume from step 3
    python referral_discover.py --list-metros      # Show available metros

Steps:
    1. Research orgs (Serper - city + ZIP search)
    2. Discover contacts (AI Ark)
    3. Enrich email + phone (BlitzAPI + Prospeo + MillionVerifier, concurrent)
    4. Classify + score (rule-based)
    5. Deduplicate + export (JSON + CSV + Google Sheets)
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


STEPS = {
    1: ("Research orgs", "1_research"),
    2: ("Discover contacts", "2_discover"),
    3: ("Enrich email + phone", "3_enrich"),
    4: ("Classify + score", "5_classify_score"),
    5: ("Dedup + export", None),  # runs 6_dedup then 7_export
}


def run_step(step_num, metro_key):
    """Run a single pipeline step."""
    name, module_name = STEPS[step_num]
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {name}")
    print(f"{'='*60}\n")

    start = time.time()

    if step_num == 5:
        # Combined dedup + export
        dedup = __import__("6_dedup")
        dedup.main(metro_key)
        export = __import__("7_export")
        export.main(metro_key)
    else:
        module = __import__(module_name)
        module.main(metro_key)

    elapsed = time.time() - start
    print(f"\n[Step {step_num} completed in {elapsed:.1f}s]")


def main():
    parser = argparse.ArgumentParser(description="Ready Rooms Referral Source Discovery")
    parser.add_argument("metro", nargs="?", default="houston", help="Metro key (default: houston)")
    parser.add_argument("--step", type=int, help="Run a specific step only (1-5)")
    parser.add_argument("--from", dest="from_step", type=int, help="Resume from step N")
    parser.add_argument("--list-metros", action="store_true", help="List available metros")
    args = parser.parse_args()

    if args.list_metros:
        from lib.config import METROS
        print("Available metros:")
        for key, metro in METROS.items():
            zips = len(metro.get("zip_codes", []))
            print(f"  {key}: {metro['city']}, {metro['state']} ({metro['county']}) - {zips} ZIPs")
        return

    # Validate metro
    from lib.config import get_metro, get_output_dir
    try:
        metro = get_metro(args.metro)
    except KeyError as e:
        print(f"Error: {e}")
        sys.exit(1)

    output_dir = get_output_dir(args.metro)
    print(f"Ready Rooms - Referral Source Discovery")
    print(f"Metro: {metro['city']}, {metro['state']}")
    print(f"Output: {output_dir}")

    total_start = time.time()

    if args.step:
        if args.step not in STEPS:
            print(f"Error: Step must be 1-5, got {args.step}")
            sys.exit(1)
        run_step(args.step, args.metro)
    else:
        start_step = args.from_step or 1
        for step_num in range(start_step, 6):
            run_step(step_num, args.metro)

    total_elapsed = time.time() - total_start
    print(f"\n{'='*60}")
    print(f"Pipeline complete in {total_elapsed/60:.1f} minutes")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
