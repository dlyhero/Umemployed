import json
import os
from datetime import datetime, timedelta
from typing import Optional, Tuple

from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Path to your credentials.json file
CREDENTIALS_FILE = os.path.join(settings.BASE_DIR, 'credentials.json')


class GoogleCalendarManager:
    """Utility class to manage Google Calendar operations for Meet scheduling"""
    
    def __init__(self, user_credentials: Optional[Credentials] = None):
        self.credentials = user_credentials
        self.service = None
        if self.credentials:
            self.service = build('calendar', 'v3', credentials=self.credentials)
    
    @staticmethod
    def get_authorization_url(request, redirect_uri: str) -> Tuple[str, str]:
        """Generate Google OAuth authorization URL"""
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent to get refresh token
        )
        
        return authorization_url, state
    
    @staticmethod
    def exchange_code_for_tokens(authorization_response: str, state: str, redirect_uri: str) -> Credentials:
        """Exchange authorization code for access tokens"""
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE,
            scopes=SCOPES,
            state=state,
            redirect_uri=redirect_uri
        )
        
        flow.fetch_token(authorization_response=authorization_response)
        return flow.credentials
    
    def create_meet_event(self, 
                         summary: str,
                         start_datetime: datetime,
                         end_datetime: datetime,
                         attendees_emails: list,
                         description: str = "") -> dict:
        """Create a Google Calendar event with Google Meet link"""
        
        if not self.service:
            raise ValueError("Google Calendar service not initialized")
        
        # Convert datetime to RFC3339 format
        start_time = start_datetime.isoformat()
        end_time = end_datetime.isoformat()
        
        # Event body
        event_body = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
            'attendees': [{'email': email} for email in attendees_emails],
            'conferenceData': {
                'createRequest': {
                    'requestId': f"meet-{datetime.now().timestamp()}",
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 10},       # 10 minutes before
                ],
            },
        }
        
        # Create the event
        event = self.service.events().insert(
            calendarId='primary',
            body=event_body,
            conferenceDataVersion=1,
            sendUpdates='all'  # Send email notifications to attendees
        ).execute()
        
        return event
    
    def refresh_credentials(self, credentials: Credentials) -> Credentials:
        """Refresh expired credentials"""
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        return credentials


def credentials_to_dict(credentials: Credentials) -> dict:
    """Convert Credentials object to dictionary for storage"""
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }


def credentials_from_dict(token_dict: dict) -> Credentials:
    """Create Credentials object from dictionary"""
    return Credentials(
        token=token_dict.get('token'),
        refresh_token=token_dict.get('refresh_token'),
        token_uri=token_dict.get('token_uri'),
        client_id=token_dict.get('client_id'),
        client_secret=token_dict.get('client_secret'),
        scopes=token_dict.get('scopes')
    )
