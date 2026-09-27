"""Robust document text extraction for PDF, DOCX, and TXT files."""
import os


class ExtractionError(Exception):
    """Raised when a file cannot be read or parsed."""


def extract_pdf_text(path: str) -> str:
    import fitz  # PyMuPDF
    try:
        doc = fitz.open(path)
    except Exception as exc:
        raise ExtractionError(f"Could not open PDF: {exc}") from exc
    try:
        text = "\n".join(page.get_text() for page in doc)
    finally:
        doc.close()
    if not text.strip():
        raise ExtractionError("PDF appears to have no extractable text (possibly scanned/image-only).")
    return text


def extract_docx_text(path: str) -> str:
    from docx import Document
    try:
        doc = Document(path)
    except Exception as exc:
        raise ExtractionError(f"Could not open DOCX: {exc}") from exc
    text = "\n".join(p.text for p in doc.paragraphs)
    if not text.strip():
        raise ExtractionError("DOCX file has no readable paragraph text.")
    return text


def extract_txt_text(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except Exception as exc:
        raise ExtractionError(f"Could not read TXT file: {exc}") from exc
    if not text.strip():
        raise ExtractionError("TXT file is empty.")
    return text


def extract_text(path: str) -> str:
    """Dispatch to the correct extractor based on file extension."""
    if not os.path.exists(path):
        raise ExtractionError(f"File not found: {path}")
    ext = path.lower().rsplit(".", 1)[-1]
    if ext == "pdf":
        return extract_pdf_text(path)
    if ext == "docx":
        return extract_docx_text(path)
    if ext == "txt":
        return extract_txt_text(path)
    raise ExtractionError(f"Unsupported file type: .{ext}")


def safe_extract_text(path: str) -> tuple[str | None, str | None]:
    """Never raises. Returns (text, error_message) — exactly one is None."""
    try:
        return extract_text(path), None
    except ExtractionError as exc:
        return None, str(exc)
    except Exception as exc:  # catch-all so one bad file never crashes a batch
        return None, f"Unexpected error: {exc}"
