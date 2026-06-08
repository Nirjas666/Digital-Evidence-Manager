import hashlib
from pathlib import Path


SUPPORTED_ALGORITHMS = {"md5", "sha1", "sha256", "sha512"}


def compute_hash(file_path, algorithm: str = "sha256"):
    """Compute the digest of a file using the specified algorithm.

    Supported algorithms: md5, sha1, sha256, sha512
    """
    algorithm = (algorithm or "sha256").lower()
    if algorithm not in SUPPORTED_ALGORITHMS:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    file_path = Path(file_path)
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    hasher = getattr(hashlib, algorithm)()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


# Backwards-compatible wrapper
def compute_sha256(file_path):
    return compute_hash(file_path, algorithm="sha256")


def verify_file(file_path, expected_hash, algorithm: str = "sha256"):
    """Verify a file against an expected hash using the given algorithm.

    Returns (matches: bool, current_hash: str)
    """
    current_hash = compute_hash(file_path, algorithm=algorithm)
    return current_hash == expected_hash, current_hash
