import json
from pathlib import Path
from typing import Any, Dict, Union


DefPath = Union[str, Path]


def save_dict_to_json(data: Dict[str, Any], path: DefPath, *, indent: int = 4, ensure_ascii: bool = False) -> None:
    """
    Save a dictionary to a JSON file.

    Args:
        data: The dictionary to save.
        path: The file path where the JSON will be saved.
        indent: Number of spaces for JSON indentation (default: 4).
        ensure_ascii: Whether to escape non-ASCII characters (default: False).
    """
    file_path = Path(path)
    # Ensure parent directory exists
    if file_path.parent:
        file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)



def load_dict_from_json(path: DefPath) -> Dict[str, Any]:
    """
    Load and return a dictionary from a JSON file.

    Args:
        path: The file path to load the JSON from.

    Returns:
        The loaded dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file contents are not valid JSON.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    with file_path.open('r', encoding='utf-8') as f:
        return json.load(f)
