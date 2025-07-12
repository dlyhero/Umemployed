"""
Google Meet Integration API Views for Next.js frontend
"""
import json
from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from ..models import Interview, GoogleCredentials, OAuthState
from ..google_utils import GoogleCalendarManager, credentials_to_dict, credentials_from_dict


class CheckGoogleConnectionAPIView(APIView):
    """Check if user has Google Calendar connected"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Check Google Calendar connection status",
        responses={
            200: openapi.Response(
                description="Connection status",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'connected': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    }
                )
            )
        }
    )
    def get(self, request):
        try:
            GoogleCredentials.objects.get(user=request.user)
            return Response({'connected': True})
        except GoogleCredentials.DoesNotExist:
            return Response({'connected': False})


class GoogleConnectAPIView(APIView):
    """Initiate Google OAuth flow for Calendar access"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get Google OAuth authorization URL",
        responses={
            200: openapi.Response(
                description="Authorization URL generated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'authorization_url': openapi.Schema(type=openapi.TYPE_STRING),
                        'state': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }
    )
    def get(self, request):
        try:
            redirect_uri = request.build_absolute_uri('/api/company/google/callback/')
            authorization_url, state = GoogleCalendarManager.get_authorization_url(request, redirect_uri)
            
            # Store OAuth state in database instead of session
            # Clean up old states for this user (older than 1 hour)
            from datetime import datetime, timedelta
            cutoff_time = datetime.now() - timedelta(hours=1)
            OAuthState.objects.filter(user=request.user, created_at__lt=cutoff_time).delete()
            
            # Store new state
            oauth_state = OAuthState.objects.create(user=request.user, state=state)
            
            # Debug logging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"OAuth Connect - Stored state in DB: {state}, User ID: {request.user.id}")
            
            return Response({
                'authorization_url': authorization_url,
                'state': state
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleOAuthCallbackAPIView(APIView):
    """Handle Google OAuth callback and store tokens"""
    permission_classes = []  # No authentication required for OAuth callback
    
    @swagger_auto_schema(
        operation_description="Handle Google OAuth callback",
        manual_parameters=[
            openapi.Parameter('code', openapi.IN_QUERY, description="Authorization code", type=openapi.TYPE_STRING),
            openapi.Parameter('state', openapi.IN_QUERY, description="State parameter", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(description="OAuth successful"),
            400: openapi.Response(description="OAuth failed")
        }
    )
    def get(self, request):
        try:
            code = request.GET.get('code')
            state = request.GET.get('state')
            
            # Debug logging to help identify the issue
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"OAuth Debug - Code: {bool(code)}, State: {state}")
            
            if not code:
                frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
                return HttpResponseRedirect(f'{frontend_url}/dashboard/settings?google_oauth=error&message=Authorization code missing')
            
            if not state:
                frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
                return HttpResponseRedirect(f'{frontend_url}/dashboard/settings?google_oauth=error&message=State parameter missing')
            
            # Look up state in database instead of session
            try:
                oauth_state = OAuthState.objects.get(state=state)
                user = oauth_state.user
                logger.error(f"OAuth Debug - Found state in DB for user: {user.id}")
            except OAuthState.DoesNotExist:
                frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
                return HttpResponseRedirect(f'{frontend_url}/dashboard/settings?google_oauth=error&message=Invalid or expired OAuth state')
            
            redirect_uri = request.build_absolute_uri('/api/company/google/callback/')
            authorization_response = request.build_absolute_uri()
            
            credentials = GoogleCalendarManager.exchange_code_for_tokens(
                authorization_response, state, redirect_uri
            )
            
            # Store credentials in database for the user
            google_creds, created = GoogleCredentials.objects.get_or_create(
                user=user,
                defaults={'credentials_json': json.dumps(credentials_to_dict(credentials))}
            )
            
            if not created:
                google_creds.credentials_json = json.dumps(credentials_to_dict(credentials))
                google_creds.save()
            
            # Clean up OAuth state
            oauth_state.delete()
            
            # Redirect to company-specific dashboard with success
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            
            # Get company ID for this user
            try:
                company_id = user.company.id
                return HttpResponseRedirect(f'{frontend_url}/companies/{company_id}/dashboard?google_oauth=success')
            except AttributeError:
                # If user doesn't have a company, redirect to general dashboard
                return HttpResponseRedirect(f'{frontend_url}/dashboard/settings?google_oauth=success')
            
        except Exception as e:
            # Redirect to frontend with error
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            return HttpResponseRedirect(f'{frontend_url}/dashboard/settings?google_oauth=error&message={str(e)}')


class DisconnectGoogleAPIView(APIView):
    """Disconnect Google Calendar integration"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Disconnect Google Calendar integration",
        responses={
            200: openapi.Response(description="Disconnected successfully"),
            404: openapi.Response(description="Not connected")
        }
    )
    def delete(self, request):
        try:
            google_creds = GoogleCredentials.objects.get(user=request.user)
            google_creds.delete()
            return Response({
                'success': True,
                'message': 'Google Calendar disconnected successfully.'
            })
        except GoogleCredentials.DoesNotExist:
            return Response({
                'success': True,
                'message': 'Google Calendar was not connected.'
            })


class CreateGoogleMeetInterviewAPIView(APIView):
    """Create an interview with Google Meet link"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Create interview with Google Meet link",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['candidate_id', 'job_title', 'date', 'time'],
            properties={
                'candidate_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'job_title': openapi.Schema(type=openapi.TYPE_STRING),
                'date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                'time': openapi.Schema(type=openapi.TYPE_STRING, format='time'),
                'timezone': openapi.Schema(type=openapi.TYPE_STRING, default='UTC'),
                'note': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(
                description="Interview created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'meeting_link': openapi.Schema(type=openapi.TYPE_STRING),
                        'event_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'interview_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            ),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Google Calendar not connected")
        }
    )
    def post(self, request):
        try:
            data = request.data
            candidate_id = data.get('candidate_id')
            job_title = data.get('job_title')
            date = data.get('date')
            time = data.get('time')
            timezone_str = data.get('timezone', 'UTC')
            note = data.get('note', '')
            
            # Validate required fields
            if not all([candidate_id, job_title, date, time]):
                return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
            
            candidate = get_object_or_404(User, id=candidate_id)
            recruiter = request.user
            
            # Check if recruiter has Google credentials
            try:
                google_creds = GoogleCredentials.objects.get(user=recruiter)
                credentials_dict = json.loads(google_creds.credentials_json)
                credentials = credentials_from_dict(credentials_dict)
            except GoogleCredentials.DoesNotExist:
                return Response({
                    "error": "Google Calendar not connected",
                    "needs_google_auth": True,
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Parse datetime
            interview_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            end_datetime = interview_datetime + timedelta(hours=1)  # Default 1 hour duration
            
            # Create Google Calendar event with Meet link
            calendar_manager = GoogleCalendarManager(credentials)
            
            event_summary = f"Interview: {job_title}"
            event_description = f"""
Interview scheduled for {job_title}
Candidate: {candidate.get_full_name() or candidate.email}
Recruiter: {recruiter.get_full_name() or recruiter.email}

Note: {note}
            """.strip()
            
            attendees = [candidate.email, recruiter.email]
            
            # Create the event
            event = calendar_manager.create_meet_event(
                summary=event_summary,
                start_datetime=interview_datetime,
                end_datetime=end_datetime,
                attendees_emails=attendees,
                description=event_description
            )
            
            # Extract Meet link from event
            meet_link = None
            if 'conferenceData' in event and 'entryPoints' in event['conferenceData']:
                for entry in event['conferenceData']['entryPoints']:
                    if entry['entryPointType'] == 'video':
                        meet_link = entry['uri']
                        break
            
            # Create interview record
            interview = Interview.objects.create(
                candidate=candidate,
                date=date,
                time=time,
                timezone=timezone_str,
                note=note,
                meeting_link=meet_link,
                google_event_id=event['id']
            )
            
            return Response({
                'success': True,
                'meeting_link': meet_link,
                'event_id': event['id'],
                'interview_id': interview.id,
                'message': 'Google Meet interview created successfully!'
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListInterviewsAPIView(APIView):
    """List interviews for the authenticated user"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="List interviews",
        responses={
            200: openapi.Response(
                description="List of interviews",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'candidate_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'date': openapi.Schema(type=openapi.TYPE_STRING),
                            'time': openapi.Schema(type=openapi.TYPE_STRING),
                            'meeting_link': openapi.Schema(type=openapi.TYPE_STRING),
                            'note': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                )
            )
        }
    )
    def get(self, request):
        try:
            # Get interviews where user is the candidate or related to user's company
            interviews = Interview.objects.filter(
                candidate=request.user
            )
            
            # If user is a recruiter, also get interviews they scheduled
            if hasattr(request.user, 'company'):
                company_interviews = Interview.objects.filter(
                    candidate__application__job__company=request.user.company
                ).distinct()
                interviews = interviews.union(company_interviews)
            
            interview_data = []
            for interview in interviews:
                interview_data.append({
                    'id': interview.id,
                    'candidate_name': interview.candidate.get_full_name() or interview.candidate.email,
                    'date': interview.date,
                    'time': interview.time,
                    'meeting_link': interview.meeting_link,
                    'note': interview.note,
                })
            
            return Response(interview_data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
