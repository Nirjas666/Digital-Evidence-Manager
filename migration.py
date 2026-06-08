from pathlib import Path
from utils import load_json, save_json
from file_hasher import SUPPORTED_ALGORITHMS


def migrate_case_metadata(case_dir: Path):
    """Non-destructive migration of case metadata files to canonical hash fields.

    - For each evidence item that contains 'sha256' but does not have 'hash'/'hash_algorithm', add them.
    - Backup the metadata.json to metadata.json.bak before modifying.
    """
    metadata_path = case_dir / "metadata.json"
    if not metadata_path.exists():
        return False

    metadata = load_json(metadata_path, None)
    if metadata is None:
        return False

    modified = False
    for ev in metadata.get("evidence", []):
        if "hash" not in ev:
            if "sha256" in ev:
                ev["hash"] = ev["sha256"]
                ev["hash_algorithm"] = "sha256"
                modified = True

    if modified:
        backup_path = case_dir / "metadata.json.bak"
        if not backup_path.exists():
            save_json(backup_path, metadata)
        save_json(metadata_path, metadata)
    return modified


def run_migration(root_dir: Path):
    case_root = root_dir / "data" / "cases"
    if not case_root.exists():
        return 0
    migrated = 0
    for case_dir in case_root.iterdir():
        if not case_dir.is_dir():
            continue
        try:
            if migrate_case_metadata(case_dir):
                migrated += 1
        except Exception:
            # skip problematic cases; do not fail the whole migration
            continue
    return migrated
