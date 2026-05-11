"""
organiser.py
------------
Core logic for scanning a directory and organising files into folders.

The organiser works in two distinct phases, which is an important
design decision:

  1. PLAN  — scan the source directory and decide where every file
             should go. No files are touched yet. The plan is returned
             as a list of Move objects.

  2. EXECUTE — carry out the plan, moving files and logging every
               action. If a move fails, it is recorded in the log
               but the rest of the plan continues.

This two-phase approach means:
  - The plan can be printed and reviewed before anything is moved
    (the --dry-run flag in main.py uses exactly this).
  - If execution is interrupted halfway, the log shows exactly which
    files were moved and which were not.
"""

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .config import build_extension_map, get_catchall_folder
from .exceptions import SourceNotFoundError, MoveError


@dataclass
class Move:
    """
    Represents a single planned file move.

    Attributes
    ----------
    source : str
        Absolute path to the file in its current location.
    destination : str
        Absolute path to where the file should be moved.
    filename : str
        The file's name (without path), for display purposes.
    category : str
        The destination folder/category name.
    extension : str
        The file's extension (lowercase), for reporting.
    """
    source: str
    destination: str
    filename: str
    category: str
    extension: str


@dataclass
class MoveResult:
    """
    Records the outcome of a single attempted file move.

    Attributes
    ----------
    move : Move
        The planned move this result corresponds to.
    success : bool
        True if the file was moved successfully.
    error : str
        Error message if the move failed; empty string on success.
    """
    move: Move
    success: bool
    error: str = ""


class FileOrganiser:
    """
    Scans a source directory and organises files by extension.

    Uses a two-phase plan → execute model. The plan can be inspected
    before execution (useful for dry runs and logging), and execution
    records a result for every planned move.

    Attributes
    ----------
    source_dir : str
        The directory to organise.
    dest_dir : str
        Root directory where category subfolders will be created.
        Defaults to source_dir if not specified.
    categories : dict[str, list[str]]
        The category configuration, as loaded by load_config().

    Examples
    --------
    >>> organiser = FileOrganiser(
    ...     source_dir="/home/user/Downloads",
    ...     dest_dir="/home/user/Organised",
    ...     categories=load_config("config.json"),
    ... )
    >>> plan = organiser.plan()
    >>> results = organiser.execute(plan)
    """

    def __init__(
        self,
        source_dir: str,
        dest_dir: str | None,
        categories: dict[str, list[str]],
    ):
        """
        Initialise the FileOrganiser.

        Parameters
        ----------
        source_dir : str
            Directory whose files will be organised.
        dest_dir : str or None
            Root output directory. If None, defaults to source_dir
            (files are organised in-place into subfolders).
        categories : dict[str, list[str]]
            Category configuration mapping folder names to extensions.

        Raises
        ------
        SourceNotFoundError
            If source_dir does not exist.
        """
        if not os.path.isdir(source_dir):
            raise SourceNotFoundError(source_dir)

        self.source_dir = os.path.abspath(source_dir)
        self.dest_dir = os.path.abspath(dest_dir) if dest_dir else self.source_dir
        self.categories = categories
        self._ext_map = build_extension_map(categories)
        self._catchall = get_catchall_folder(categories)

    def plan(self) -> list[Move]:
        """
        Scan the source directory and build a list of planned moves.

        Only files directly inside source_dir are considered —
        subdirectories are not recursed into, keeping the organiser's
        scope predictable. Hidden files (starting with ".") are skipped.

        Returns
        -------
        list[Move]
            One Move object per file found. Files that are already in
            the destination directory are excluded to avoid loops.
        """
        moves = []

        for entry in sorted(os.scandir(self.source_dir), key=lambda e: e.name):
            if not entry.is_file():
                continue
            if entry.name.startswith("."):
                continue  # Skip hidden files.

            ext = Path(entry.name).suffix.lower()
            category = self._ext_map.get(ext, self._catchall)
            dest_folder = os.path.join(self.dest_dir, category)
            destination = self._resolve_destination(entry.path, dest_folder, entry.name)

            moves.append(Move(
                source=entry.path,
                destination=destination,
                filename=entry.name,
                category=category,
                extension=ext if ext else "(no extension)",
            ))

        return moves

    def execute(self, plan: list[Move]) -> list[MoveResult]:
        """
        Execute a list of planned moves, recording the result of each.

        Destination folders are created as needed. If a move fails,
        a MoveResult with success=False is recorded and execution
        continues with the remaining files.

        Parameters
        ----------
        plan : list[Move]
            A plan as returned by FileOrganiser.plan().

        Returns
        -------
        list[MoveResult]
            One result per planned move, in the same order.
        """
        results = []

        for move in plan:
            os.makedirs(os.path.dirname(move.destination), exist_ok=True)
            try:
                shutil.move(move.source, move.destination)
                results.append(MoveResult(move=move, success=True))
            except OSError as e:
                results.append(MoveResult(
                    move=move,
                    success=False,
                    error=str(e),
                ))

        return results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _resolve_destination(
        self, source_path: str, dest_folder: str, filename: str
    ) -> str:
        """
        Compute a safe destination path, avoiding overwrites.

        If a file with the same name already exists in the destination,
        a numeric suffix is added: "photo.jpg" → "photo_1.jpg" → etc.

        Parameters
        ----------
        source_path : str
            The source file's absolute path (used to detect if the
            file is already in the destination folder).
        dest_folder : str
            The destination folder path.
        filename : str
            The file's name.

        Returns
        -------
        str
            A safe absolute destination path with no collision.
        """
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        candidate = os.path.join(dest_folder, filename)

        counter = 1
        while os.path.exists(candidate) and candidate != source_path:
            candidate = os.path.join(dest_folder, f"{stem}_{counter}{suffix}")
            counter += 1

        return candidate
