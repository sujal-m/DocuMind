import os
from typing import List, Dict, Any, Tuple
import pymupdf as fitz
import docx
from backend.app.core.logging import logger

class ExtractionError(Exception):
    """Custom exception raised when document extraction fails or yields no extractable text."""
    pass

class ExtractionService:
    @staticmethod
    def extract_pdf(file_path: str) -> Tuple[List[Dict[str, Any]], int]:
        """
        Extracts text from PDF documents using PyMuPDF (fitz) page-by-page.
        Returns:
            (pages, total_pages) where pages is a list of {'page_number': int, 'text': str}
        """
        if not os.path.exists(file_path):
            raise ExtractionError(f"PDF file not found at path: {file_path}")

        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            if total_pages == 0:
                raise ExtractionError("PDF document has 0 pages.")

            pages_data = []
            total_extracted_chars = 0

            for page_idx in range(total_pages):
                page = doc.load_page(page_idx)
                text = page.get_text("text").strip()
                if text:
                    total_extracted_chars += len(text)
                    pages_data.append({
                        "page_number": page_idx + 1,
                        "text": text
                    })

            doc.close()

            if not pages_data or total_extracted_chars == 0:
                raise ExtractionError(
                    "No extractable text found in PDF. The document may be empty, image-only, or password protected."
                )

            logger.info(f"Extracted {total_extracted_chars} characters from {len(pages_data)} pages in {file_path}")
            return pages_data, total_pages

        except Exception as e:
            if isinstance(e, ExtractionError):
                raise
            raise ExtractionError(f"Failed to extract text from PDF: {str(e)}") from e

    @staticmethod
    def extract_docx(file_path: str) -> Tuple[List[Dict[str, Any]], int]:
        """
        Extracts text from DOCX files using python-docx.
        Since Word docs do not have native fixed page breaks until rendered,
        we group paragraphs into logical sections or page estimates.
        """
        if not os.path.exists(file_path):
            raise ExtractionError(f"DOCX file not found at path: {file_path}")

        try:
            doc = docx.Document(file_path)
            text_blocks = []

            # Extract paragraphs
            for p in doc.paragraphs:
                cleaned = p.text.strip()
                if cleaned:
                    text_blocks.append(cleaned)

            # Extract table contents
            for table in doc.tables:
                for row in table.rows:
                    row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_cells:
                        text_blocks.append(" | ".join(row_cells))

            if not text_blocks:
                raise ExtractionError("DOCX document contains no text.")

            # Chunk into estimated pages (~2500 characters per page)
            full_text = "\n\n".join(text_blocks)
            chars_per_page = 2500
            pages_data = []
            total_pages = max(1, (len(full_text) + chars_per_page - 1) // chars_per_page)

            for i in range(total_pages):
                start = i * chars_per_page
                end = min(len(full_text), (i + 1) * chars_per_page)
                page_text = full_text[start:end].strip()
                if page_text:
                    pages_data.append({
                        "page_number": i + 1,
                        "text": page_text
                    })

            logger.info(f"Extracted {len(full_text)} characters from DOCX into {len(pages_data)} sections: {file_path}")
            return pages_data, total_pages

        except Exception as e:
            if isinstance(e, ExtractionError):
                raise
            raise ExtractionError(f"Failed to extract text from DOCX: {str(e)}") from e

    @staticmethod
    def extract_txt(file_path: str) -> Tuple[List[Dict[str, Any]], int]:
        """
        Extracts text from plain text files with encoding fallback (UTF-8, Latin-1, CP1252).
        """
        if not os.path.exists(file_path):
            raise ExtractionError(f"TXT file not found at path: {file_path}")

        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
        content = None

        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    content = f.read()
                    break
            except UnicodeDecodeError:
                continue

        if content is None:
            raise ExtractionError("Failed to decode text file with standard encodings.")

        cleaned = content.strip()
        if not cleaned:
            raise ExtractionError("Text file is empty.")

        # Estimate pages based on 2500 chars per page
        chars_per_page = 2500
        total_pages = max(1, (len(cleaned) + chars_per_page - 1) // chars_per_page)
        pages_data = []

        for i in range(total_pages):
            start = i * chars_per_page
            end = min(len(cleaned), (i + 1) * chars_per_page)
            page_text = cleaned[start:end].strip()
            if page_text:
                pages_data.append({
                    "page_number": i + 1,
                    "text": page_text
                })

        logger.info(f"Extracted {len(cleaned)} characters from TXT file: {file_path}")
        return pages_data, total_pages

    @classmethod
    def extract(cls, file_path: str, file_type: str) -> Tuple[List[Dict[str, Any]], int]:
        """
        Route to appropriate extractor based on normalized file_type (pdf, docx, txt).
        """
        norm_type = file_type.lower().lstrip(".")
        if norm_type == "pdf":
            return cls.extract_pdf(file_path)
        elif norm_type == "docx":
            return cls.extract_docx(file_path)
        elif norm_type == "txt":
            return cls.extract_txt(file_path)
        else:
            raise ExtractionError(f"Unsupported file type: {norm_type}")
