import os
import re
from fastapi import HTTPException, status
from backend.app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
}

def sanitize_filename(filename: str) -> str:
    """
    Remove potentially dangerous characters and path traversal segments.
    """
    # Strip directory components
    clean = os.path.basename(filename)
    # Remove null bytes and non-printable characters
    clean = re.sub(r'[\x00-\x1f\x7f]', '', clean)
    # Replace spaces and tricky characters with underscore or dash
    clean = re.sub(r'[^a-zA-Z0-9_\.\-]', '_', clean)
    # Ensure it's not empty
    if not clean or clean.startswith('.'):
        clean = f"document_{clean.lstrip('.')}"
    return clean

def validate_file_metadata(filename: str, file_size: int, content_type: str = None) -> str:
    """
    Validates file extension, MIME type, and size constraints.
    Returns the normalized extension.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    return ext

