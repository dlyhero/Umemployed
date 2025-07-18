#!/usr/bin/env python
"""
Test Script for Enhanced Job Creation Step 4

This script tests the enhanced job creation step 4 functionality including:
- Progress tracking
- Notification timing
- Retry functionality
- Error handling
"""

import os
import sys
import django
import time
import requests
import json

# Setup Django environment
sys.path.append('/home/nyuydine/Documents/UM/Umemployed')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umemployed.settings')
django.setup()

from job.models import Job, Skill, SkillGenerationStatus
from users.models import User
from notifications.models import Notification


def test_job_creation_step4():
    """Test the enhanced job creation step 4 functionality"""
    
    print("=" * 60)
    print("TESTING ENHANCED JOB CREATION STEP 4")
    print("=" * 60)
    
    # Test 1: Check notification timing
    print("\n1. Testing Notification Timing...")
    test_notification_timing()
    
    # Test 2: Check progress tracking
    print("\n2. Testing Progress Tracking...")
    test_progress_tracking()
    
    # Test 3: Check retry functionality
    print("\n3. Testing Retry Functionality...")
    test_retry_functionality()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)


def test_notification_timing():
    """Test that notifications are only sent when job is complete"""
    
    # Find a job that's in progress
    in_progress_jobs = Job.objects.filter(
        is_available=True,
        job_creation_is_complete=False
    ).first()
    
    if not in_progress_jobs:
        print("   ⚠️  No in-progress jobs found for testing")
        return
    
    # Check if there are premature notifications
    premature_notifications = Notification.objects.filter(
        user=in_progress_jobs.user,
        notification_type=Notification.NEW_JOB_POSTED,
        message__contains=in_progress_jobs.title
    )
    
    if premature_notifications.exists():
        print(f"   ❌ Found {premature_notifications.count()} premature notifications")
        for notif in premature_notifications:
            print(f"      - {notif.message} (created: {notif.timestamp})")
    else:
        print("   ✅ No premature notifications found")
    
    # Check if there are completion notifications for incomplete jobs
    completion_notifications = Notification.objects.filter(
        user=in_progress_jobs.user,
        notification_type=Notification.NEW_JOB_POSTED,
        message__contains="complete"
    )
    
    if completion_notifications.exists():
        print(f"   ❌ Found {completion_notifications.count()} completion notifications for incomplete job")
    else:
        print("   ✅ No completion notifications for incomplete jobs")


def test_progress_tracking():
    """Test progress tracking functionality"""
    
    # Find jobs with skill generation statuses
    jobs_with_status = Job.objects.filter(
        skill_statuses__isnull=False
    ).distinct()[:3]
    
    if not jobs_with_status:
        print("   ⚠️  No jobs with skill statuses found for testing")
        return
    
    for job in jobs_with_status:
        print(f"   📊 Job: {job.title}")
        
        # Get skill statuses
        statuses = SkillGenerationStatus.objects.filter(job=job)
        
        total_skills = job.requirements.count()
        completed_skills = statuses.filter(
            status__in=['ai_success', 'fallback_used', 'generic_used', 'experience_based']
        ).count()
        processing_skills = statuses.filter(
            status__in=['in_progress', 'pending']
        ).count()
        failed_skills = statuses.filter(
            status__in=['ai_failed', 'manual_required']
        ).count()
        
        percentage = (completed_skills / total_skills * 100) if total_skills > 0 else 0
        
        print(f"      Skills: {completed_skills}/{total_skills} complete ({percentage:.1f}%)")
        print(f"      Processing: {processing_skills}, Failed: {failed_skills}")
        
        # Check if progress tracking is working
        if job.questions_generation_progress:
            tracked_skills = len(job.questions_generation_progress)
            print(f"      Progress tracking: {tracked_skills} skills tracked")
        else:
            print(f"      Progress tracking: No progress data")


def test_retry_functionality():
    """Test retry functionality for failed skills"""
    
    # Find failed skills
    failed_skills = SkillGenerationStatus.objects.filter(
        status__in=['ai_failed', 'manual_required']
    )[:5]
    
    if not failed_skills:
        print("   ⚠️  No failed skills found for testing")
        return
    
    print(f"   🔄 Found {failed_skills.count()} failed skills:")
    
    for status_obj in failed_skills:
        print(f"      - {status_obj.skill.name} in job '{status_obj.job.title}'")
        print(f"        Status: {status_obj.status}")
        print(f"        AI Attempts: {status_obj.ai_attempts}")
        if status_obj.error_message:
            print(f"        Error: {status_obj.error_message[:50]}...")
        
        # Check if retry is possible
        if status_obj.ai_attempts < 3:
            print(f"        ✅ Can retry (attempts: {status_obj.ai_attempts}/3)")
        else:
            print(f"        ❌ Max attempts reached")


def check_job_completion_logic():
    """Check job completion logic"""
    
    print("\n4. Checking Job Completion Logic...")
    
    # Find jobs that should be complete but aren't
    incomplete_jobs = Job.objects.filter(
        is_available=True,
        job_creation_is_complete=False
    )
    
    for job in incomplete_jobs[:3]:
        print(f"   📋 Job: {job.title}")
        
        total_skills = job.requirements.count()
        if total_skills == 0:
            print(f"      ⚠️  No skills required - should be complete")
            continue
        
        # Check skill statuses
        statuses = SkillGenerationStatus.objects.filter(job=job)
        completed_skills = statuses.filter(
            status__in=['ai_success', 'fallback_used', 'generic_used', 'experience_based']
        ).count()
        
        if completed_skills == total_skills:
            print(f"      ❌ All skills complete but job not marked complete")
            print(f"         Skills: {completed_skills}/{total_skills}")
        else:
            print(f"      ✅ Correctly incomplete: {completed_skills}/{total_skills} skills ready")


def generate_test_report():
    """Generate a comprehensive test report"""
    
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST REPORT")
    print("=" * 60)
    
    # Overall statistics
    total_jobs = Job.objects.count()
    complete_jobs = Job.objects.filter(job_creation_is_complete=True).count()
    available_jobs = Job.objects.filter(is_available=True).count()
    
    print(f"Total Jobs: {total_jobs}")
    print(f"Complete Jobs: {complete_jobs}")
    print(f"Available Jobs: {available_jobs}")
    print(f"Completion Rate: {(complete_jobs/total_jobs)*100:.1f}%" if total_jobs > 0 else "N/A")
    
    # Skill generation statistics
    total_statuses = SkillGenerationStatus.objects.count()
    successful_statuses = SkillGenerationStatus.objects.filter(
        status__in=['ai_success', 'fallback_used', 'generic_used', 'experience_based']
    ).count()
    failed_statuses = SkillGenerationStatus.objects.filter(
        status__in=['ai_failed', 'manual_required']
    ).count()
    
    print(f"\nSkill Generation:")
    print(f"Total Skills: {total_statuses}")
    print(f"Successful: {successful_statuses}")
    print(f"Failed: {failed_statuses}")
    print(f"Success Rate: {(successful_statuses/total_statuses)*100:.1f}%" if total_statuses > 0 else "N/A")
    
    # Notification statistics
    total_notifications = Notification.objects.filter(
        notification_type=Notification.NEW_JOB_POSTED
    ).count()
    
    print(f"\nNotifications:")
    print(f"Job Posted Notifications: {total_notifications}")


if __name__ == "__main__":
    try:
        test_job_creation_step4()
        check_job_completion_logic()
        generate_test_report()
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc() 