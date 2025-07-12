#!/usr/bin/env python
"""
Test script to debug Google OAuth flow
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umemployed.settings')
django.setup()

from company.google_utils import GoogleCalendarManager

def test_oauth_scopes():
    """Test what scopes are being used"""
    print("=== Google OAuth Scope Test ===")
    
    # Check Django settings
    from django.conf import settings
    scopes = getattr(settings, 'SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE', [])
    print(f"Django settings scopes: {scopes}")
    
    # Check what GoogleCalendarManager is using
    from company.google_utils import SCOPES
    print(f"GoogleCalendarManager scopes: {SCOPES}")
    
    # Test authorization URL generation
    try:
        class MockRequest:
            def build_absolute_uri(self, path):
                return f"http://localhost:8000{path}"
        
        mock_request = MockRequest()
        redirect_uri = mock_request.build_absolute_uri('/api/company/google/callback/')
        print(f"Redirect URI: {redirect_uri}")
        
        auth_url, state = GoogleCalendarManager.get_authorization_url(mock_request, redirect_uri)
        print(f"Authorization URL generated successfully")
        print(f"State: {state}")
        print(f"Auth URL: {auth_url}")
        
        # Test if the redirect URI is in credentials
        import json
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
            registered_uris = creds['web']['redirect_uris']
            print(f"\nRegistered redirect URIs in credentials.json:")
            for uri in registered_uris:
                print(f"  - {uri}")
            
            if redirect_uri in registered_uris:
                print(f"✅ Redirect URI '{redirect_uri}' is registered")
            else:
                print(f"❌ Redirect URI '{redirect_uri}' is NOT registered")
        
        # Parse the authorization URL to see what scopes are being requested
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(auth_url)
        query_params = parse_qs(parsed_url.query)
        requested_scopes = query_params.get('scope', [''])[0].split(' ')
        print(f"\nScopes in authorization URL:")
        for scope in requested_scopes:
            if scope:
                print(f"  - {scope}")
        
    except Exception as e:
        print(f"Error generating authorization URL: {e}")
        import traceback
        traceback.print_exc()

def test_azure_redirect():
    """Test Azure redirect URI"""
    print("\n=== Azure Redirect URI Test ===")
    
    class MockAzureRequest:
        def build_absolute_uri(self, path):
            return f"https://umemployed-f6fdddfffmhjhjcj.canadacentral-01.azurewebsites.net{path}"
    
    mock_request = MockAzureRequest()
    redirect_uri = mock_request.build_absolute_uri('/api/company/google/callback/')
    print(f"Azure Redirect URI: {redirect_uri}")
    
    try:
        auth_url, state = GoogleCalendarManager.get_authorization_url(mock_request, redirect_uri)
        print(f"✅ Azure authorization URL generated successfully")
        print(f"State: {state}")
        
        # Check if Azure URI is registered
        import json
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
            registered_uris = creds['web']['redirect_uris']
            
            if redirect_uri in registered_uris:
                print(f"✅ Azure redirect URI '{redirect_uri}' is registered")
            else:
                print(f"❌ Azure redirect URI '{redirect_uri}' is NOT registered")
                print("You need to add this URI to your Google Cloud Console")
        
    except Exception as e:
        print(f"❌ Error with Azure redirect URI: {e}")

def test_oauth_consent_screen():
    """Test Google OAuth consent screen configuration"""
    print("\n=== OAuth Consent Screen Test ===")
    
    import json
    with open('credentials.json', 'r') as f:
        creds = json.load(f)
        client_id = creds['web']['client_id']
        print(f"Client ID: {client_id}")
        
    print("\n🔍 Things to check in Google Cloud Console:")
    print("1. OAuth consent screen configuration:")
    print("   - Go to: APIs & Services > OAuth consent screen")
    print("   - Publishing status should be 'In production' or 'Testing'")
    print("   - Scopes should include:")
    print("     • openid")
    print("     • /auth/userinfo.email")
    print("     • /auth/userinfo.profile") 
    print("     • /auth/calendar.events")
    print("\n2. API enablement:")
    print("   - Go to: APIs & Services > Library")
    print("   - Ensure these APIs are enabled:")
    print("     • Google Calendar API")
    print("     • Google+ API (for userinfo)")

def test_oauth_flow_simulation():
    """Simulate what happens during OAuth flow"""
    print("\n=== OAuth Flow Simulation ===")
    
    # Test with the exact same parameters that would be used in production
    class MockProductionRequest:
        def build_absolute_uri(self, path):
            return f"https://umemployed-f6fdddfffmhjhjcj.canadacentral-01.azurewebsites.net{path}"
    
    mock_request = MockProductionRequest()
    redirect_uri = mock_request.build_absolute_uri('/api/company/google/callback/')
    
    try:
        auth_url, state = GoogleCalendarManager.get_authorization_url(mock_request, redirect_uri)
        
        print(f"Production OAuth URL:")
        print(f"  Redirect URI: {redirect_uri}")
        print(f"  State: {state}")
        
        # Extract and verify all parameters
        from urllib.parse import urlparse, parse_qs, unquote
        parsed_url = urlparse(auth_url)
        params = parse_qs(parsed_url.query)
        
        print(f"\n📋 OAuth Parameters:")
        print(f"  response_type: {params.get('response_type', [''])[0]}")
        print(f"  client_id: {params.get('client_id', [''])[0]}")
        print(f"  redirect_uri: {unquote(params.get('redirect_uri', [''])[0])}")
        print(f"  scope: {unquote(params.get('scope', [''])[0])}")
        print(f"  state: {params.get('state', [''])[0]}")
        print(f"  access_type: {params.get('access_type', [''])[0]}")
        print(f"  include_granted_scopes: {params.get('include_granted_scopes', [''])[0]}")
        print(f"  prompt: {params.get('prompt', [''])[0]}")
        
        # Check scope format
        scope_param = unquote(params.get('scope', [''])[0])
        scopes = scope_param.split(' ')
        
        expected_scopes = [
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile', 
            'https://www.googleapis.com/auth/calendar.events'
        ]
        
        print(f"\n🔍 Scope Verification:")
        for expected_scope in expected_scopes:
            if expected_scope in scopes:
                print(f"  ✅ {expected_scope}")
            else:
                print(f"  ❌ {expected_scope} - MISSING!")
        
        # Check for extra scopes
        for scope in scopes:
            if scope and scope not in expected_scopes:
                print(f"  ⚠️  Extra scope: {scope}")
        
        print(f"\n🌐 Test this URL manually:")
        print(f"Copy and paste this URL into a browser:")
        print(f"{auth_url}")
        print(f"\nExpected behavior:")
        print(f"1. Should redirect to Google OAuth consent screen")
        print(f"2. Should show all 4 scopes for permission")
        print(f"3. After consent, should redirect back to your callback URL")
        
    except Exception as e:
        print(f"❌ Error in OAuth flow simulation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_oauth_scopes()
    test_azure_redirect()
    test_oauth_consent_screen()
    test_oauth_flow_simulation()
