import docx
import fitz
import os
import pytest

from app.services.extractor import DocumentExtractor


def create_dummy_pdf(path: str, text: str):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    doc.save(path)
    doc.close()

def create_dummy_docx(path: str, text: str):
    doc = docx.Document()
    doc.add_paragraph(text)
    doc.save(path)

def create_dummy_txt(path: str, text: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

@pytest.fixture
def dummy_files(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    docx_path = tmp_path / "test.docx"
    txt_path = tmp_path / "test.txt"

    create_dummy_pdf(str(pdf_path), "Hello PDF")
    create_dummy_docx(str(docx_path), "Hello DOCX")
    create_dummy_txt(str(txt_path), "Hello TXT")

    return {
        "pdf": str(pdf_path),
        "docx": str(docx_path),
        "txt": str(txt_path)
    }

def test_extract_pdf(dummy_files):
    text = DocumentExtractor.extract_text(dummy_files["pdf"])
    assert "Hello PDF" in text

def test_extract_docx(dummy_files):
    text = DocumentExtractor.extract_text(dummy_files["docx"])
    assert "Hello DOCX" in text

def test_extract_txt(dummy_files):
    text = DocumentExtractor.extract_text(dummy_files["txt"])
    assert "Hello TXT" in text

def test_unsupported_file(dummy_files):
    unknown_path = dummy_files["txt"].replace(".txt", ".unknown")
    with open(unknown_path, "w") as f:
        f.write("test")
    with pytest.raises(ValueError):
        DocumentExtractor.extract_text(unknown_path)
    os.remove(unknown_path)

def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        DocumentExtractor.extract_text("nonexistent_file.pdf")
