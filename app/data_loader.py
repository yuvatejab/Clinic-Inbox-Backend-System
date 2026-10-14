
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def load_json(filename: str) -> dict[str, Any]:
    """Load a JSON object from the project's data directory."""
    path = DATA_DIR / filename

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Required data file not found: {path}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in {path}, line {exc.lineno}: {exc.msg}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {path}")

    return data


def load_jsonl(filename: str) -> list[dict[str, Any]]:
    """Load JSON objects from a JSONL file, preserving file order."""
    path = DATA_DIR / filename
    records: list[dict[str, Any]] = []

    try:
        with path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue

                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSON in {path}, "
                        f"line {line_number}: {exc.msg}"
                    ) from exc

                if not isinstance(record, dict):
                    raise ValueError(
                        f"Expected a JSON object in {path}, "
                        f"line {line_number}"
                    )

                records.append(record)

    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Required data file not found: {path}"
        ) from exc

    return records
