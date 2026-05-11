"""
reporter.py
-----------
Generates a summary report and console output for an organiser run.

Kept separate from the organiser so that display logic never pollutes
business logic. The reporter can be swapped out (e.g. for a GUI
progress bar) without touching the organiser or config modules.
"""

import os
from collections import defaultdict
from datetime import datetime

from .organiser import Move, MoveResult


def print_plan(plan: list[Move]) -> None:
    """
    Print a dry-run preview of all planned moves to the console.

    Parameters
    ----------
    plan : list[Move]
        The plan as returned by FileOrganiser.plan().
    """
    if not plan:
        print("  Nothing to organise — source directory is empty.")
        return

    print(f"\n  {'FILE':<40} {'CATEGORY':<15} {'EXTENSION'}")
    print(f"  {'-'*40} {'-'*15} {'-'*10}")

    for move in plan:
        name = move.filename if len(move.filename) <= 38 else move.filename[:35] + "..."
        print(f"  {name:<40} {move.category:<15} {move.extension}")

    print(f"\n  Total: {len(plan)} file(s) would be moved.")


def print_results(results: list[MoveResult]) -> None:
    """
    Print a live summary of what was moved during execution.

    Parameters
    ----------
    results : list[MoveResult]
        The results as returned by FileOrganiser.execute().
    """
    success_count = sum(1 for r in results if r.success)
    fail_count = len(results) - success_count

    for result in results:
        icon = "✓" if result.success else "✗"
        dest_folder = os.path.basename(os.path.dirname(result.move.destination))
        print(f"  [{icon}] {result.move.filename:<40} → {dest_folder}/")
        if not result.success:
            print(f"       ERROR: {result.error}")

    print(f"\n  Moved: {success_count}   Failed: {fail_count}")


def generate_report(
    results: list[MoveResult],
    source_dir: str,
    dest_dir: str,
    output_path: str,
) -> None:
    """
    Write a full organiser run report to a text file.

    Includes an overview, a per-category breakdown, and a complete
    file-by-file move log.

    Parameters
    ----------
    results : list[MoveResult]
        The results as returned by FileOrganiser.execute().
    source_dir : str
        The source directory path (for display in the report).
    dest_dir : str
        The destination root directory (for display in the report).
    output_path : str
        Full path where the .txt report file will be saved.
    """
    lines = []
    sep = "=" * 60
    success_count = sum(1 for r in results if r.success)
    fail_count = len(results) - success_count

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    lines += [
        sep,
        "  FILE ORGANISER — RUN REPORT",
        sep,
        f"  Run at        : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"  Source dir    : {source_dir}",
        f"  Destination   : {dest_dir}",
        "",
    ]

    # ------------------------------------------------------------------
    # Overview
    # ------------------------------------------------------------------
    lines += [
        "  OVERVIEW",
        "-" * 60,
        f"  Files processed : {len(results):>5}",
        f"  Successfully moved: {success_count:>3}",
        f"  Failed          : {fail_count:>5}",
        "",
    ]

    # ------------------------------------------------------------------
    # Per-category breakdown
    # ------------------------------------------------------------------
    by_category: dict[str, list[MoveResult]] = defaultdict(list)
    for result in results:
        by_category[result.move.category].append(result)

    lines += [
        "  FILES BY CATEGORY",
        "-" * 60,
        f"  {'Category':<20} {'Files':>6}  {'OK':>4}  {'Failed':>6}",
        f"  {'-'*20} {'-'*6}  {'-'*4}  {'-'*6}",
    ]

    for category in sorted(by_category.keys()):
        cat_results = by_category[category]
        ok = sum(1 for r in cat_results if r.success)
        fail = len(cat_results) - ok
        lines.append(
            f"  {category:<20} {len(cat_results):>6}  {ok:>4}  {fail:>6}"
        )

    lines.append("")

    # ------------------------------------------------------------------
    # Full move log
    # ------------------------------------------------------------------
    lines += [
        "  MOVE LOG",
        "-" * 60,
    ]

    for result in results:
        status = "OK  " if result.success else "FAIL"
        lines.append(
            f"  [{status}] {result.move.filename}"
            f"\n         → {result.move.destination}"
        )
        if not result.success:
            lines.append(f"         ERROR: {result.error}")

    lines.append("")

    # ------------------------------------------------------------------
    # Footer
    # ------------------------------------------------------------------
    lines += [sep, "  END OF REPORT", sep]

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"  Report saved → {output_path}")
