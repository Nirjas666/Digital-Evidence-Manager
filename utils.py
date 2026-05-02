import json
import os
from datetime import datetime
from pathlib import Path


def ensure_dir(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default if default is not None else {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        return default if default is not None else {}


def save_json(path, data):
    path = Path(path)
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def format_timestamp(timestamp=None):
    if timestamp is None:
        timestamp = datetime.utcnow()
    if isinstance(timestamp, datetime):
        return timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
    return str(timestamp)


def normalize_tags(tags):
    if not tags:
        return []
    if isinstance(tags, str):
        tags = [tag.strip().lower() for tag in tags.split(",") if tag.strip()]
    else:
        tags = [str(tag).strip().lower() for tag in tags]
    return sorted(set(tags))
