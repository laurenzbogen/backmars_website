"""
Prints upcoming events from a Google Calendar that contain #public
in the title or description. Runs once and exits.

Setup:
  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
  Put your OAuth client file next to this script as credentials.json
"""
import html
import os
import re
from datetime import datetime, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from zoneinfo import ZoneInfo

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CALENDAR_ID = "primary"   # or the band calendar's ID
TAG = re.compile(r"(?<!\w)#public(?!\w)", re.IGNORECASE)


def event_date(event, fmt_date="%d.%m.%y", fmt_time="%H:%M"):
    start = event["start"]
    if "dateTime" not in start:                       # all-day event: only "date"
        return datetime.fromisoformat(start["date"]).strftime(fmt_date)
    dt = datetime.fromisoformat(start["dateTime"])    # handles "+02:00" and "Z"
    if start.get("timeZone"):                         # show the event's own local time
        dt = dt.astimezone(ZoneInfo(start["timeZone"]))
    return dt.strftime(f"{fmt_date} {fmt_time}")

def get_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)


def fetch(service, **time_range):
    items = service.events().list(
        calendarId=CALENDAR_ID, singleEvents=True, orderBy="startTime", **time_range
    ).execute().get("items", [])
    return [
            {"title": TAG.sub("", e["summary"]).strip(), "descr": e.get("description", ""), "date": event_date(e)}
        for e in items
        if TAG.search(e.get("summary", ""))
    ]


def get_events():
    service = get_service()
    now = datetime.now(timezone.utc).isoformat()
    future = fetch(service, timeMin=now)
    past = fetch(service, timeMax=now)

    return future, past
