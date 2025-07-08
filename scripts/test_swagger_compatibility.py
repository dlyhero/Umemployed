#!/usr/bin/env python3
"""
Simple script to test if the Swagger schema generation issue is resolved.
This script mimics what happens during Swagger schema generation.
"""

import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
project_root = "/home/nyuydine/Documents/UM/Umemployed"
sys.path.insert(0, project_root)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umemployed.settings')
django.setup()

from job.api.views import RecruiterJobListAPIView, RecruiterJobDetailAPIView, SavedJobsListAPIView, AppliedJobsListAPIView
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

def test_swagger_compatibility():
    """Test that views handle Swagger schema generation without errors."""
    
    print("Testing Swagger compatibility for job API views...")
    
    # Create a fake request with AnonymousUser (like during schema generation)
    factory = RequestFactory()
    request = factory.get('/')
    request.user = AnonymousUser()
    
    views_to_test = [
        ('RecruiterJobListAPIView', RecruiterJobListAPIView),
        ('RecruiterJobDetailAPIView', RecruiterJobDetailAPIView),
        ('SavedJobsListAPIView', SavedJobsListAPIView),
        ('AppliedJobsListAPIView', AppliedJobsListAPIView),
    ]
    
    for view_name, view_class in views_to_test:
        try:
            # Simulate what happens during schema generation
            view = view_class()
            view.request = request
            view.swagger_fake_view = True  # This is what drf-yasg sets
            
            # Try to call get_queryset (which caused the original error)
            if hasattr(view, 'get_queryset'):
                queryset = view.get_queryset()
                print(f"✅ {view_name}: get_queryset() works - returned {queryset}")
            else:
                print(f"✅ {view_name}: No get_queryset method (APIView)")
                
        except Exception as e:
            print(f"❌ {view_name}: Error - {e}")
            return False
    
    print("\n🎉 All views are now Swagger-compatible!")
    return True

if __name__ == "__main__":
    test_swagger_compatibility()
