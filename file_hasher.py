import hashlib
from pathlib import Path


def compute_sha256(file_path):
    file_path = Path(file_path)
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    sha256 = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def verify_file(file_path, expected_hash):
    current_hash = compute_sha256(file_path)
    return current_hash == expected_hash, current_hash
