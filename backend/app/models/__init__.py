import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)  # pdf, docx, txt
    file_size = Column(Integer, nullable=False)     # in bytes
    file_hash = Column(String(64), nullable=False, index=True) # SHA-256
    page_count = Column(Integer, nullable=True, default=1)
    chunk_count = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="pending")  # pending, processing, indexed, error
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=False, default=1)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False, default=0)
    faiss_id = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    document = relationship("Document", back_populates="chunks")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False, default="New Research Session")
    model_name = Column(String(64), nullable=False, default="gemini-2.5-flash")
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    tool_calls_json = Column(Text, nullable=True)   # JSON string for agent tool execution trace
    citations_json = Column(Text, nullable=True)    # JSON string for verified chunk references
    created_at = Column(DateTime, default=utc_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")

