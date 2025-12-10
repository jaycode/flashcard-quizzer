"""File handling utilities for flashcard quizzer."""

import json
from typing import Any
from pathlib import Path


def load_json_file(filepath: str) -> Any:
    """
    Load and parse a JSON file.

    Args:
        filepath: Path to the JSON file

    Returns:
        Parsed JSON data

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If JSON is invalid
    """
    file_path = Path(filepath)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {filepath}: {e}")
    except Exception as e:
        raise ValueError(f"Error reading file {filepath}: {e}")
