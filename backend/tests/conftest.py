import os
import pytest
import fitz
import docx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.session import Base, get_db
from backend.app.main import app
from backend.app.core.config import settings

TEST_UPLOAD_DIR = os.path.join(settings.DATA_DIR, "test_uploads")
TEST_VECTOR_DIR = os.path.join(settings.DATA_DIR, "test_vector")
os.makedirs(TEST_UPLOAD_DIR, exist_ok=True)
os.makedirs(TEST_VECTOR_DIR, exist_ok=True)

# In-memory SQLite engine for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_pdf_path(tmp_path):
    path = tmp_path / "sample_test.pdf"
    doc = fitz.open()
    # Page 1
    p1 = doc.new_page()
    p1.insert_text((50, 72), "DocuMind Research Overview. This document describes AI document intelligence.")
    # Page 2
    p2 = doc.new_page()
    p2.insert_text((50, 72), "Retrieval-Augmented Generation (RAG) grounds responses using vector similarity.")
    doc.save(str(path))
    doc.close()
    return str(path)

@pytest.fixture
def sample_docx_path(tmp_path):
    path = tmp_path / "sample_test.docx"
    doc = docx.Document()
    doc.add_heading("DocuMind Contract Specifications", level=1)
    doc.add_paragraph("This agreement governs artificial intelligence research workflows.")
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Clause"
    table.cell(0, 1).text = "Value"
    table.cell(1, 0).text = "Service Level"
    table.cell(1, 1).text = "99.9% uptime"
    doc.save(str(path))
    return str(path)

@pytest.fixture
def sample_txt_path(tmp_path):
    path = tmp_path / "sample_test.txt"
    with open(str(path), "w", encoding="utf-8") as f:
        f.write("Section 1: Introduction\nDocuMind processes heterogeneous documents.\n\nSection 2: Methodology\nUsing FAISS and Sentence Transformers.")
    return str(path)

