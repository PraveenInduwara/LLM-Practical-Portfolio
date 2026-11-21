from __future__ import annotations

import base64
import json
import os
from datetime import date, datetime, time, timedelta
from email.mime.text import MIMEText
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo


TIMEZONE = ZoneInfo("Asia/Colombo")
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/gmail.send",
]


class GoogleSetupError(RuntimeError):
    pass


class GoogleWorkspace:
    """Optional Google Workspace APIs; OAuth is requested only when a tool is used."""

    def __init__(self, confirm: Callable[[str], bool] | None = None):
        self.confirm = confirm or (lambda _: False)
        base = Path(__file__).resolve().parents[1]
        self.credentials_path = Path(os.getenv("GOOGLE_OAUTH_CLIENT_FILE", base / "credentials.json")).expanduser()
        self.token_path = Path(os.getenv("GOOGLE_OAUTH_TOKEN_FILE", base / "data" / "google_token.json")).expanduser()
        if not self.credentials_path.is_absolute():
            self.credentials_path = (base / self.credentials_path).resolve()
        if not self.token_path.is_absolute():
            self.token_path = (base / self.token_path).resolve()
        self._credentials = None
        self._services = {}

    def _service(self, api: str, version: str):
        if api in self._services:
            return self._services[api]
        if not self.credentials_path.is_file():
            raise GoogleSetupError(
                f"Google OAuth is not configured. Put a Google Desktop OAuth client JSON at "
                f"{self.credentials_path} or set GOOGLE_OAUTH_CLIENT_FILE."
            )
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise GoogleSetupError(
                "Install Lab 6 requirements first (google-api-python-client, google-auth-oauthlib)."
            ) from exc

        credentials = None
        if self.token_path.is_file():
            credentials = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_path), SCOPES)
                credentials = flow.run_local_server(port=0)
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            self.token_path.write_text(credentials.to_json(), encoding="utf-8")
        self._credentials = credentials
        self._services[api] = build(api, version, credentials=credentials, cache_discovery=False)
        return self._services[api]

    @staticmethod
    def _parse_datetime(value: str) -> datetime:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.replace(tzinfo=TIMEZONE) if dt.tzinfo is None else dt.astimezone(TIMEZONE)

    def calendar_today(self) -> str:
        now = datetime.now(TIMEZONE)
        start = datetime.combine(now.date(), time.min, tzinfo=TIMEZONE)
        end = start + timedelta(days=1)
        service = self._service("calendar", "v3")
        events = service.events().list(
            calendarId="primary", timeMin=start.isoformat(), timeMax=end.isoformat(),
            singleEvents=True, orderBy="startTime", maxResults=50,
        ).execute().get("items", [])
        if not events:
            return f"No calendar events were returned for {now.date().isoformat()} (Asia/Colombo)."
        lines = [f"Today's events in Asia/Colombo ({now.date().isoformat()}):"]
        for event in events:
            start_value = event.get("start", {}).get("dateTime", event.get("start", {}).get("date", "time unknown"))
            lines.append(f"- {start_value}: {event.get('summary', '(untitled event)')}")
        return "\n".join(lines)

    def create_calendar_event(self, summary: str, start: str, end: str, description: str = "") -> str:
        start_dt, end_dt = self._parse_datetime(start), self._parse_datetime(end)
        if end_dt <= start_dt:
            return "Event was not created: end time must be later than start time."
        preview = f"Create Calendar event {summary!r} from {start_dt.isoformat()} to {end_dt.isoformat()}?"
        if not self.confirm(preview):
            return "Event creation cancelled; no calendar changes were made."
        service = self._service("calendar", "v3")
        result = service.events().insert(calendarId="primary", body={
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "Asia/Colombo"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "Asia/Colombo"},
        }).execute()
        return f"Created calendar event {result.get('summary', summary)!r}; event id {result.get('id', 'unknown')}."

    def read_sheet(self, spreadsheet_id: str, range_name: str) -> str:
        service = self._service("sheets", "v4")
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name
        ).execute()
        rows = result.get("values", [])
        return json.dumps(rows, ensure_ascii=False, indent=2) if rows else "The requested range is empty."

    def update_sheet(self, spreadsheet_id: str, range_name: str, values_json: str) -> str:
        try:
            values = json.loads(values_json)
        except json.JSONDecodeError as exc:
            return f"Sheet was not updated: values must be valid JSON: {exc}"
        if not isinstance(values, list) or any(not isinstance(row, list) for row in values):
            return "Sheet was not updated: values_json must be a JSON array of row arrays."
        if not self.confirm(f"Update Google Sheet range {range_name!r} with {len(values)} row(s)?"):
            return "Sheet update cancelled; no spreadsheet changes were made."
        result = self._service("sheets", "v4").spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body={"values": values},
        ).execute()
        return f"Updated {result.get('updatedCells', 0)} Google Sheets cell(s)."

    def create_doc(self, title: str, content: str) -> str:
        if not self.confirm(f"Create Google Doc {title!r} ({len(content)} characters)?"):
            return "Document creation cancelled; no Google Doc was created."
        docs = self._service("docs", "v1")
        document = docs.documents().create(body={"title": title}).execute()
        document_id = document["documentId"]
        docs.documents().batchUpdate(documentId=document_id, body={
            "requests": [{"insertText": {"location": {"index": 1}, "text": content}}]
        }).execute()
        return f"Created Google Doc {title!r}; document id {document_id}."

    def send_gmail(self, to: str, subject: str, body: str) -> str:
        message = MIMEText(body, "plain", "utf-8")
        message["to"], message["subject"] = to, subject
        encoded = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")
        if not self.confirm(f"Send Gmail to {to!r} with subject {subject!r}?"):
            return "Email cancelled; no message was sent."
        result = self._service("gmail", "v1").users().messages().send(
            userId="me", body={"raw": encoded}
        ).execute()
        return f"Sent Gmail message; message id {result.get('id', 'unknown')}."

