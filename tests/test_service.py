"""Tests for the orchestrating service."""

from __future__ import annotations

import io

from pypdf import PdfWriter

from pdf_agent.config import Settings
from pdf_agent.service import PdfAgentService


def _blank_pdf() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def test_process_blank_pdf_skips_integrations() -> None:
    service = PdfAgentService(Settings())
    result = service.process_bytes(_blank_pdf(), filename="blank.pdf")

    assert result["filename"] == "blank.pdf"
    assert result["slack"]["status"] == "skipped"
    assert result["calendar"]["status"] == "skipped"
    assert "No text" in result["summary"]


def test_summarizer_heuristic() -> None:
    from pdf_agent.summarizer import Summarizer

    summarizer = Summarizer(Settings())
    result = summarizer.summarize(
        "Quarterly revenue grew 12%. Costs were reduced. Action: hire two engineers."
    )
    assert set(result) >= {"summary", "key_insights", "action_items"}
    assert result["summary"]
