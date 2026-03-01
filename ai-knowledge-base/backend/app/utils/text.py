from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader


def extract_text_from_txt(content: bytes) -> str:
    return content.decode("utf-8", errors="ignore")


def extract_text_from_pdf(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    texts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(texts)
