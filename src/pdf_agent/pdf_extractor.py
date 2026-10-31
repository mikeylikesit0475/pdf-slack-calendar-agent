"""PDF text extraction utilities."""

from __future__ import annotations

import io
from typing import BinaryIO

from pypdf import PdfReader


def extract_text(source: bytes | BinaryIO) -> str:
    """Extract plain text from a PDF given raw bytes or a file-like object."""

    if hasattr(source, "read"):
        data = source.read()  # type: ignore[union-attr]
    else:
        data = source  # type: ignore[assignment]

    reader = PdfReader(io.BytesIO(data))
    pages: list[str] = []
    for idx, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:  # pragma: no cover - defensive
            text = ""
        pages.append(f"--- Page {idx} ---\n{text.strip()}")
    return "\n\n".join(pages).strip()
