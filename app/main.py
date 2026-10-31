"""FastAPI entrypoint for the PDF agent."""

from __future__ import annotations

from typing import Annotated, Optional

from fastapi import FastAPI, File, Form, UploadFile

from pdf_agent.service import PdfAgentService

app = FastAPI(title="PDF Slack Calendar Agent", version="0.1.0")
_service = PdfAgentService()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/process")
async def process_pdf(
    file: UploadFile = File(...),
    meeting_start: Optional[str] = Form(None),
    duration_minutes: int = Form(30),
) -> dict:
    data = await file.read()
    return _service.process_bytes(
        data,
        filename=file.filename or "document.pdf",
        meeting_start=meeting_start,
        duration_minutes=duration_minutes,
    )
