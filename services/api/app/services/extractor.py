import logging
import os

import docx
import fitz  # PyMuPDF
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class DocumentExtractor:
    """Service responsible for extracting raw text from various document formats."""

    @staticmethod
    def extract_text(file_path: str, mime_type: str | None = None) -> str:
        """
        Extracts text from a given file path based on its extension or mime type.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == ".pdf" or mime_type == "application/pdf":
                return DocumentExtractor._extract_from_pdf(file_path)
            elif ext == ".docx" or mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return DocumentExtractor._extract_from_docx(file_path)
            elif ext == ".txt" or mime_type == "text/plain":
                return DocumentExtractor._extract_from_txt(file_path)
            elif ext in [".html", ".htm"] or mime_type == "text/html":
                return DocumentExtractor._extract_from_html(file_path)
            else:
                raise ValueError(f"Unsupported file extension: {ext}")
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e!s}")
            raise

    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        text_parts = []
        with fitz.open(file_path) as doc:
            for page in doc:
                text_parts.append(page.get_text())
        return "\n".join(text_parts)

    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    @staticmethod
    def _extract_from_txt(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    @staticmethod
    def _extract_from_html(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            return soup.get_text(separator="\n", strip=True)
