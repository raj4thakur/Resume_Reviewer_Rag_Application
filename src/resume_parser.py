from __future__ import annotations

from io import BytesIO
from typing import BinaryIO

import fitz
from docx import Document


MAX_TEXT_CHARS = 60_000


def _read_pdf(data: bytes) -> str:
    doc = fitz.open(stream=data, filetype="pdf")
    try:
        return "\n".join(page.get_text("text") for page in doc)
    finally:
        doc.close()


def _read_docx(data: bytes) -> str:
    document = Document(BytesIO(data))
    chunks = [p.text for p in document.paragraphs if p.text.strip()]
    for table in document.tables:
        for row in table.rows:
            chunks.append(" | ".join(cell.text.strip() for cell in row.cells))
    return "\n".join(chunks)


def extract_text_from_upload(uploaded_file: BinaryIO) -> str:
    name = getattr(uploaded_file, "name", "").lower()
    data = uploaded_file.getvalue()

    if not data:
        raise ValueError(f"{name or 'File'} is empty.")

    if name.endswith(".pdf"):
        text = _read_pdf(data)
    elif name.endswith(".docx"):
        text = _read_docx(data)
    elif name.endswith(".txt"):
        text = data.decode("utf-8", errors="replace")
    else:
        raise ValueError("Unsupported file type. Use PDF, DOCX, or TXT.")

    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if not text:
        raise ValueError(f"No readable text was found in {name or 'the uploaded file'}.")

    return text[:MAX_TEXT_CHARS]
