import json
from pathlib import Path


def load_schema(path: str | None) -> dict:
    """
    Load schema from JSON file.
    If path is None, return an empty dict.
    
    Schema format:
    {
        "email": {"type": "email"},
        "tanggal": {"type": "date"},
        "nama": {"type": "text"}
    }
    """
    if path is None:
        return {}

    schema_path = Path(path)
    with schema_path.open('r', encoding='utf-8') as f:
        schema = json.load(f)

    if not isinstance(schema, dict):
        raise ValueError("Schema must be a JSON object")

    return schema
