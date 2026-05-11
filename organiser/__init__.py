"""
File Organiser — sorts files in a directory into category subfolders.
Fully configurable via a JSON config file, with dry-run support.
"""

from .organiser import FileOrganiser, Move, MoveResult
from .config import load_config, build_extension_map
from .reporter import print_plan, print_results, generate_report
from .exceptions import OrganiserError, SourceNotFoundError, ConfigError, MoveError

__version__ = "1.0.0"
__author__ = "Daniel Dobos"

__all__ = [
    "FileOrganiser",
    "Move",
    "MoveResult",
    "load_config",
    "build_extension_map",
    "print_plan",
    "print_results",
    "generate_report",
    "OrganiserError",
    "SourceNotFoundError",
    "ConfigError",
    "MoveError",
]
