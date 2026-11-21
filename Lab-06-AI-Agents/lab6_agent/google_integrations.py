from __future__ import annotations

import os
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo


TIMEZONE = ZoneInfo("Asia/Colombo")
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.events.readonly",
]


class GoogleSetupError(RuntimeError):
    pass


class GoogleCalendar:
    """Optional Google Calendar API using a user-authorized desktop OAuth client."""

    def __init__(self, confirm: Callable[[str], bool] | None = None):
        self.confirm = confirm or (lambda _: False)
        base = Path(__file__).resolve().parents[1]
        self.credentials_path = Path(os.getenv("GOOGLE_OAUTH_CLIENT_FILE", base / "credentials.json")).expanduser()
        self.token_path = Path(os.getenv("GOOGLE_OAUTH_TOKEN_FILE", base / "data" / "google_token.json")).expanduser()
        if not self.credentials_path.is_absolute():
            self.credentials_path = (base / self.credentials_path).resolve()
        if not self.token_path.is_absolute():
            self.token_path = (base / self.token_path).resolve()
        self._service_instance = None

    def _service(self):
        if self._service_instance is not None:
            return self._service_instance
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
        self._service_instance = build("calendar", "v3", credentials=credentials, cache_discovery=False)
        return self._service_instance

    @staticmethod
    def _parse_datetime(value: str) -> datetime:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.replace(tzinfo=TIMEZONE) if parsed.tzinfo is None else parsed.astimezone(TIMEZONE)

    def calendar_today(self) -> str:
        now = datetime.now(TIMEZONE)
        start = datetime.combine(now.date(), time.min, tzinfo=TIMEZONE)
        end = start + timedelta(days=1)
        events = self._service().events().list(
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
        event = self._service().events().insert(calendarId="primary", body={
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "Asia/Colombo"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "Asia/Colombo"},
        }).execute()
        return f"Created calendar event {event.get('summary', summary)!r}; event id {event.get('id', 'unknown')}."
