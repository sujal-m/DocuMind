import hashlib

def calculate_sha256(file_bytes: bytes) -> str:
    """
    Computes standard SHA-256 checksum of raw file bytes for duplicate detection.
    """
    hasher = hashlib.sha256()
    hasher.update(file_bytes)
    return hasher.hexdigest()

