"""Google Calendar scheduling helper."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build


def schedule_meeting(
    service_account_file: str | None,
    calendar_id: str,
    title: str,
    description: str,
    meeting_start: str | None = None,
    duration_minutes: int = 30,
    attendees: list[str] | None = None,
) -> dict[str, Any]:
    if not service_account_file:
        return {"status": "skipped", "reason": "GOOGLE_SERVICE_ACCOUNT_FILE not configured"}

    if meeting_start:
        start = datetime.fromisoformat(meeting_start.replace("Z", "+00:00"))
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
    else:
        start = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

    end = start + timedelta(minutes=duration_minutes)

    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=["https://www.googleapis.com/auth/calendar"],
    )
    service = build("calendar", "v3", credentials=credentials, cache_discovery=False)

    event = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end.isoformat(), "timeZone": "UTC"},
    }
    if attendees:
        event["attendees"] = [{"email": email} for email in attendees]

    created = service.events().insert(calendarId=calendar_id, body=event).execute()
    return {
        "status": "created",
        "event_id": created.get("id"),
        "html_link": created.get("htmlLink"),
        "start": start.isoformat(),
    }
