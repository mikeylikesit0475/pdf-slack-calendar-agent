"""Summarization and insight extraction."""

from __future__ import annotations

import json
import re
from typing import Any

import requests

from .config import Settings


class Summarizer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def summarize(self, text: str) -> dict[str, Any]:
        text = text[: self.settings.summary_max_chars]
        body_for_check = re.sub(r"---\s*Page \d+\s*---", "", text)
        if not body_for_check.strip():
            return self._empty()
        if not text.strip():
            return self._empty()
        if self.settings.openai_api_key:
            try:
                return self._openai(text)
            except Exception:
                pass
        return self._heuristic(text)

    def _empty(self) -> dict[str, Any]:
        return {
            "summary": "No text could be extracted from the document.",
            "key_insights": [],
            "action_items": [],
            "suggested_meeting_title": "Document review",
            "suggested_meeting_description": "",
        }

    def _openai(self, text: str) -> dict[str, Any]:
        prompt = (
            "Analyze the following document and respond with strict JSON containing: "
            "summary (string), key_insights (list of strings), action_items (list of strings), "
            "suggested_meeting_title (string), suggested_meeting_description (string)."
        )
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
            json={
                "model": self.settings.openai_model,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2,
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return {
            "summary": str(parsed.get("summary", "")).strip(),
            "key_insights": [str(x).strip() for x in parsed.get("key_insights", []) if str(x).strip()],
            "action_items": [str(x).strip() for x in parsed.get("action_items", []) if str(x).strip()],
            "suggested_meeting_title": str(parsed.get("suggested_meeting_title", "Document review")).strip(),
            "suggested_meeting_description": str(parsed.get("suggested_meeting_description", "")).strip(),
        }

    def _heuristic(self, text: str) -> dict[str, Any]:
        # Strip page markers for analysis.
        body = re.sub(r"---\s*Page \d+\s*---", "", text)
        sentences = re.split(r"(?<=[.!?])\s+", body.strip())
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        summary = " ".join(sentences[:5]).strip()
        if len(summary) > 600:
            summary = summary[:597] + "..."

        insights = []
        for line in body.splitlines():
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith(("-", "*", "•"))):
                insights.append(line.lstrip("-*•0123456789. ").strip())
        insights = [i for i in insights if len(i) > 10][:8]

        if not insights and sentences:
            insights = sentences[:5]

        action_items = [i for i in insights if re.search(r"\b(must|should|need|action|todo|next)\b", i, re.I)][:5]

        title = "Document review"
        match = re.search(r"(?im)^(title|subject)\s*[:\-]\s*(.+)$", body)
        if match:
            title = match.group(2).strip()[:80]

        return {
            "summary": summary or body[:500].strip(),
            "key_insights": insights,
            "action_items": action_items,
            "suggested_meeting_title": title,
            "suggested_meeting_description": summary,
        }
