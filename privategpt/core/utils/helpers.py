"""Helper utility functions."""

import os
from pathlib import Path
from typing import Union
import unicodedata


def validate_file_path(file_path: Union[str, Path]) -> Path:
    """Validate and convert file path to Path object."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    return path


def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """Get file size in megabytes."""
    path = Path(file_path)
    size_bytes = path.stat().st_size
    return round(size_bytes / (1024 * 1024), 2)


def sanitize_filename(filename: str) -> str:
    """Remove or replace invalid characters from filename."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()


def ensure_directory_exists(directory: Union[str, Path]) -> Path:
    """Ensure directory exists, create if it doesn't."""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path

def normalize_text(text: str) -> str:
    """Lowercase and remove accents for robust matching."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])