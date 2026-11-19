from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class ChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chunk_index: int
    page_number: int
    content: str
    token_count: int
    faiss_id: Optional[int] = None

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    original_name: str
    file_type: str
    file_size: int
    file_hash: str
    page_count: Optional[int] = 1
    chunk_count: int = 0
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class DocumentDetailResponse(DocumentResponse):
    chunks: List[ChunkResponse] = []

class DocumentUploadResponse(BaseModel):
    message: str
    document: DocumentResponse
    is_duplicate: bool = False

class DocumentStatusResponse(BaseModel):
    id: str
    original_name: str
    status: str
    chunk_count: int
    error_message: Optional[str] = None
