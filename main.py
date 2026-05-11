"""
main.py
-------
Entry point for the File Organiser.

Usage:
    # Organise using built-in default rules
    python main.py --source data/sample_downloads

    # Preview what WOULD happen without moving anything
    python main.py --source data/sample_downloads --dry-run

    # Use a custom category config file
    python main.py --source data/sample_downloads --config my_config.json

    # Organise into a separate destination directory
    python main.py --source data/sample_downloads --dest data/organised
"""

import argparse
import os
import sys

from organiser.config import load_config
from organiser.organiser import FileOrganiser
from organiser.reporter import print_plan, print_results, generate_report
from organiser.exceptions import OrganiserError


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SOURCE = os.path.join(BASE_DIR, "data", "sample_downloads")
DEFAULT_REPORT = os.path.join(BASE_DIR, "data", "organiser_report.txt")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Organise files in a directory into category subfolders.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --source ~/Downloads
  python main.py --source ~/Downloads --dry-run
  python main.py --source ~/Downloads --config my_rules.json --dest ~/Sorted
        """,
    )
    parser.add_argument(
        "--source",
        default=DEFAULT_SOURCE,
        metavar="PATH",
        help="Directory to organise (default: data/sample_downloads/)",
    )
    parser.add_argument(
        "--dest",
        default=None,
        metavar="PATH",
        help="Destination root (default: same as --source)",
    )
    parser.add_argument(
        "--config",
        default=None,
        metavar="FILE",
        help="Path to a custom JSON config file (default: built-in rules)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be moved without actually moving anything",
    )
    return parser.parse_args()


def run() -> None:
    """Execute the file organiser pipeline."""
    args = parse_args()

    print("=" * 60)
    print("  FILE ORGANISER")
    print("=" * 60)
    print(f"  Source  : {args.source}")
    print(f"  Dest    : {args.dest or args.source + ' (in-place)'}")
    print(f"  Config  : {args.config or 'built-in defaults'}")
    print(f"  Mode    : {'DRY RUN — no files will be moved' if args.dry_run else 'LIVE'}")
    print()

    # ------------------------------------------------------------------
    # Load config
    # ------------------------------------------------------------------
    try:
        categories = load_config(args.config)
    except OrganiserError as e:
        print(f"  ERROR: {e.message}")
        sys.exit(1)

    print(f"  Loaded {len(categories)} categories: {', '.join(categories.keys())}")
    print()

    # ------------------------------------------------------------------
    # Build plan
    # ------------------------------------------------------------------
    try:
        organiser = FileOrganiser(
            source_dir=args.source,
            dest_dir=args.dest,
            categories=categories,
        )
    except OrganiserError as e:
        print(f"  ERROR: {e.message}")
        sys.exit(1)

    print("Planning...")
    plan = organiser.plan()

    if not plan:
        print("  Nothing to organise — source directory is empty or has no files.")
        sys.exit(0)

    print_plan(plan)

    # ------------------------------------------------------------------
    # Dry run: stop here
    # ------------------------------------------------------------------
    if args.dry_run:
        print("\n  DRY RUN complete — no files were moved.")
        sys.exit(0)

    # ------------------------------------------------------------------
    # Execute
    # ------------------------------------------------------------------
    print("\nMoving files...")
    results = organiser.execute(plan)
    print_results(results)

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------
    print("\nGenerating report...")
    generate_report(
        results=results,
        source_dir=organiser.source_dir,
        dest_dir=organiser.dest_dir,
        output_path=DEFAULT_REPORT,
    )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    success = sum(1 for r in results if r.success)
    print("\n" + "=" * 60)
    print("  COMPLETE")
    print("=" * 60)
    print(f"  Files moved     : {success} / {len(results)}")
    print(f"  Report saved    : {DEFAULT_REPORT}")
    print("=" * 60)


if __name__ == "__main__":
    run()
