"""
config.py
---------
Loads and validates the organiser's category configuration.

The config is a plain JSON file that maps folder names to lists of
file extensions. This means the organiser is completely rule-driven —
you change behaviour by editing config.json, not the code itself.

Default config (used when no custom file is provided):

    {
        "Images":     [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"],
        "Documents":  [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".csv", ".pptx"],
        "Audio":      [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
        "Video":      [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv"],
        "Code":       [".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".sh"],
        "Archives":   [".zip", ".tar", ".gz", ".rar", ".7z"],
        "Misc":       []
    }

"Misc" with an empty list is special — it acts as the catch-all
category for any extension not matched by the other rules.
"""

import json
import os

from .exceptions import ConfigError


# Sensible defaults — works out of the box without any config file.
DEFAULT_CATEGORIES: dict[str, list[str]] = {
    "Images":    [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".tiff"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls", ".csv",
                  ".pptx", ".ppt", ".odt", ".rtf"],
    "Audio":     [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"],
    "Video":     [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm"],
    "Code":      [".py", ".js", ".ts", ".html", ".css", ".json", ".xml",
                  ".sh", ".yaml", ".yml", ".toml", ".md", ".ipynb"],
    "Archives":  [".zip", ".tar", ".gz", ".rar", ".7z", ".bz2"],
    "Misc":      [],   # Catch-all — must stay last conceptually.
}


def load_config(config_path: str | None = None) -> dict[str, list[str]]:
    """
    Load category configuration from a JSON file, or return defaults.

    Parameters
    ----------
    config_path : str or None
        Path to a JSON config file. If None or the file does not
        exist, the built-in DEFAULT_CATEGORIES are returned.

    Returns
    -------
    dict[str, list[str]]
        Mapping of folder name → list of lowercase file extensions.
        Extensions are normalised to lowercase with a leading dot.

    Raises
    ------
    ConfigError
        If the file exists but is not valid JSON, or if the top-level
        structure is not a dict mapping strings to lists.
    """
    if config_path is None or not os.path.exists(config_path):
        return DEFAULT_CATEGORIES.copy()

    try:
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"'{config_path}' is not valid JSON — {e}")
    except OSError as e:
        raise ConfigError(f"Could not read '{config_path}' — {e}")

    if not isinstance(data, dict):
        raise ConfigError("Config file must be a JSON object at the top level.")

    # Normalise: folder names to strings, extensions to lowercase with dot.
    normalised: dict[str, list[str]] = {}
    for folder, extensions in data.items():
        if not isinstance(extensions, list):
            raise ConfigError(
                f"Extensions for '{folder}' must be a JSON array, "
                f"got {type(extensions).__name__}."
            )
        normalised[str(folder)] = [
            ext.lower() if ext.startswith(".") else f".{ext.lower()}"
            for ext in extensions
        ]

    return normalised


def build_extension_map(categories: dict[str, list[str]]) -> dict[str, str]:
    """
    Invert the categories dict into an extension → folder lookup map.

    Having both representations is useful:
    - categories  : folder → [extensions]  — good for display / config editing
    - extension map: extension → folder    — good for fast per-file lookup

    Parameters
    ----------
    categories : dict[str, list[str]]
        As returned by load_config().

    Returns
    -------
    dict[str, str]
        Maps each extension (e.g. ".pdf") to its destination folder
        name (e.g. "Documents"). Extensions in the "Misc" category
        (the catch-all, marked with an empty list) are not included —
        "Misc" is looked up by absence rather than by key.
    """
    ext_map: dict[str, str] = {}

    for folder, extensions in categories.items():
        for ext in extensions:
            ext_map[ext.lower()] = folder

    return ext_map


def get_catchall_folder(categories: dict[str, list[str]]) -> str:
    """
    Find the catch-all folder name (the one with an empty extension list).

    Parameters
    ----------
    categories : dict[str, list[str]]
        As returned by load_config().

    Returns
    -------
    str
        The name of the catch-all folder, or "Misc" if none is defined.
    """
    for folder, extensions in categories.items():
        if not extensions:
            return folder
    return "Misc"
