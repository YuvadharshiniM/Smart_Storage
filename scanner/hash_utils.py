from pathlib import Path
import hashlib


def generate_file_hash(file_path: str) -> str:
    """Generate a SHA-256 hash for a file based on its binary content.

    Args:
        file_path (str): Path to the file as a string.

    Returns:
        str: Hex digest of the SHA-256 hash, or an empty string on error.
    """
    path = Path(file_path)

    if not path.is_file():
        return ""

    sha256 = hashlib.sha256()

    try:
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                sha256.update(chunk)
    except (OSError, IOError):
        return ""

    return sha256.hexdigest()
