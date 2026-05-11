"""
exceptions.py
-------------
Custom exception classes for the File Organiser package.
"""


class OrganiserError(Exception):
    """Base exception for all File Organiser errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class SourceNotFoundError(OrganiserError):
    """Raised when the source directory does not exist."""

    def __init__(self, path: str):
        self.path = path
        super().__init__(f"Source directory not found: '{path}'")


class ConfigError(OrganiserError):
    """Raised when the configuration file is missing or malformed."""

    def __init__(self, detail: str):
        super().__init__(f"Configuration error: {detail}")


class MoveError(OrganiserError):
    """Raised when a file cannot be moved to its destination."""

    def __init__(self, src: str, dst: str, reason: str = ""):
        self.src = src
        self.dst = dst
        super().__init__(
            f"Could not move '{src}' → '{dst}'"
            + (f" — {reason}" if reason else "")
        )
