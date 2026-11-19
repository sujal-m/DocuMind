import pytest
from backend.app.services.extraction_service import ExtractionService, ExtractionError

def test_extract_pdf(sample_pdf_path):
    pages, total = ExtractionService.extract_pdf(sample_pdf_path)
    assert total == 2
    assert len(pages) == 2
    assert pages[0]["page_number"] == 1
    assert "DocuMind Research Overview" in pages[0]["text"]
    assert pages[1]["page_number"] == 2
    assert "Retrieval-Augmented Generation" in pages[1]["text"]

def test_extract_docx(sample_docx_path):
    pages, total = ExtractionService.extract_docx(sample_docx_path)
    assert total >= 1
    full_text = " ".join([p["text"] for p in pages])
    assert "DocuMind Contract Specifications" in full_text
    assert "99.9% uptime" in full_text

def test_extract_txt(sample_txt_path):
    pages, total = ExtractionService.extract_txt(sample_txt_path)
    assert total >= 1
    full_text = " ".join([p["text"] for p in pages])
    assert "Section 1: Introduction" in full_text
    assert "Sentence Transformers" in full_text

def test_empty_file_fails(tmp_path):
    empty_txt = tmp_path / "empty.txt"
    empty_txt.write_text("", encoding="utf-8")
    with pytest.raises(ExtractionError):
        ExtractionService.extract_txt(str(empty_txt))

