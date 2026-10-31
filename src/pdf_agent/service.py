"""End-to-end orchestration for the PDF agent."""

from __future__ import annotations

from typing import Any

from .calendar_scheduler import schedule_meeting
from .config import Settings
from .pdf_extractor import extract_text
from .slack_notifier import send_summary
from .summarizer import Summarizer


class PdfAgentService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()
        self.summarizer = Summarizer(self.settings)

    def process_bytes(
        self,
        pdf_bytes: bytes,
        filename: str = "document.pdf",
        meeting_start: str | None = None,
        duration_minutes: int = 30,
        attendees: list[str] | None = None,
    ) -> dict[str, Any]:
        text = extract_text(pdf_bytes)
        insights = self.summarizer.summarize(text)

        payload = {
            "filename": filename,
            "summary": insights["summary"],
            "key_insights": insights["key_insights"],
            "action_items": insights["action_items"],
        }

        slack_result = send_summary(self.settings.slack_webhook_url, payload)

        meeting_title = insights.get("suggested_meeting_title") or f"Review: {filename}"
        meeting_description = insights.get("suggested_meeting_description") or insights["summary"]
        calendar_result = schedule_meeting(
            self.settings.google_service_account_file,
            self.settings.google_calendar_id,
            meeting_title,
            meeting_description,
            meeting_start=meeting_start,
            duration_minutes=duration_minutes,
            attendees=attendees,
        )

        return {
            "filename": filename,
            "characters_extracted": len(text),
            "summary": insights["summary"],
            "key_insights": insights["key_insights"],
            "action_items": insights["action_items"],
            "suggested_meeting_title": meeting_title,
            "slack": slack_result,
            "calendar": calendar_result,
        }
