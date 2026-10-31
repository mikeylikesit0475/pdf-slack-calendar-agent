"""Configuration helpers for the PDF agent."""

import os
from dataclasses import dataclass


@dataclass
class Settings:
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    slack_webhook_url: str | None = None
    google_service_account_file: str | None = None
    google_calendar_id: str = "primary"
    summary_max_chars: int = 12000

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL") or None,
            google_service_account_file=os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or None,
            google_calendar_id=os.getenv("GOOGLE_CALENDAR_ID", "primary"),
            summary_max_chars=int(os.getenv("SUMMARY_MAX_CHARS", "12000")),
        )
