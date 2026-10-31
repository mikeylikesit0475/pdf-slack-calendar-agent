# PDF → Slack → Calendar Agent

FastAPI service that reads a PDF, extracts key insights, posts a summary to Slack,
and schedules a follow-up meeting in Google Calendar.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in .env with your credentials.
PYTHONPATH=src uvicorn app.main:app --reload --port 8001
```

## Environment variables

- `OPENAI_API_KEY` (optional) — enables LLM summarization; falls back to heuristics.
- `OPENAI_MODEL` (default `gpt-4o-mini`)
- `SLACK_WEBHOOK_URL` — Slack incoming webhook.
- `GOOGLE_SERVICE_ACCOUNT_FILE` — path to service account JSON.
- `GOOGLE_CALENDAR_ID` (default `primary`)
- `SUMMARY_MAX_CHARS` (default `12000`)

## Usage

```bash
curl -F "file=@report.pdf" http://localhost:8000/process
```

Optional form fields: `meeting_start` (ISO 8601), `duration_minutes`.

## Tests

```bash
pytest -q
```
EOF