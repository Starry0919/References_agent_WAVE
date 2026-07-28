from pathlib import Path

try:
    from ..schema import sha256_file
except ImportError:
    from schema import sha256_file


def verify_checksum(path: Path, expected: str) -> bool:
    return path.is_file() and sha256_file(path) == expected

