from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.document import (
    DocumentResponse,
    DocumentUploadResponse,
    DocumentStatusResponse,
    DocumentDetailResponse,
    ChunkResponse
)
from backend.app.services.document_service import DocumentService
from backend.app.database.repositories.chunk_repo import ChunkRepository

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a PDF, DOCX, or TXT document.
    Validates file integrity, detects duplicates via SHA-256, and begins background indexing.
    """
    service = DocumentService(db)
    doc, is_duplicate = await service.upload_document(file, background_tasks)

    msg = "Document already indexed (duplicate detected)." if is_duplicate else "Document uploaded and queued for processing."
    return DocumentUploadResponse(
        message=msg,
        document=DocumentResponse.model_validate(doc),
        is_duplicate=is_duplicate
    )

@router.get("", response_model=List[DocumentResponse])
def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all uploaded documents with current processing status.
    """
    service = DocumentService(db)
    docs = service.list_documents(skip=skip, limit=limit)
    return [DocumentResponse.model_validate(d) for d in docs]

@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed document record including associated chunk metadata.
    """
    service = DocumentService(db)
    doc = service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    chunk_repo = ChunkRepository(db)
    chunks = chunk_repo.get_by_document_id(document_id)

    doc_data = DocumentResponse.model_validate(doc).model_dump()
    doc_data["chunks"] = [ChunkResponse.model_validate(c) for c in chunks]
    return DocumentDetailResponse(**doc_data)

@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
def get_document_status(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Lightweight polling endpoint for real-time document processing progress.
    """
    service = DocumentService(db)
    doc = service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return DocumentStatusResponse(
        id=doc.id,
        original_name=doc.original_name,
        status=doc.status,
        chunk_count=doc.chunk_count,
        error_message=doc.error_message
    )

@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Cascading delete of a document: purges uploaded file, database records, and FAISS vectors.
    """
    service = DocumentService(db)
    success = service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return {"message": f"Document '{document_id}' and all associated vectors deleted successfully."}

@router.post("/{document_id}/reindex", response_model=DocumentResponse)
def reindex_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Re-extracts, re-chunks, and re-indexes an existing document from scratch.
    """
    service = DocumentService(db)
    doc = service.reindex_document(document_id, background_tasks)
    return DocumentResponse.model_validate(doc)

