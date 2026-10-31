"""Slack notification helper."""

from __future__ import annotations

from typing import Any

import requests


def send_summary(webhook_url: str | None, payload: dict[str, Any]) -> dict[str, Any]:
    if not webhook_url:
        return {"status": "skipped", "reason": "SLACK_WEBHOOK_URL not configured"}

    summary = payload.get("summary", "")
    insights = payload.get("key_insights", [])
    actions = payload.get("action_items", [])
    filename = payload.get("filename", "document.pdf")

    blocks_text = "\n".join(f"• {item}" for item in insights) or "• (none extracted)"
    actions_text = "\n".join(f"• {item}" for item in actions) or "• (none)"

    message = (
        f"*PDF Summary: {filename}*\n\n"
        f"*Summary*\n{summary}\n\n"
        f"*Key Insights*\n{blocks_text}\n\n"
        f"*Action Items*\n{actions_text}"
    )

    response = requests.post(webhook_url, json={"text": message}, timeout=10)
    response.raise_for_status()
    return {"status": "sent", "http_status": response.status_code}
