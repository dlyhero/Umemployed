#!/usr/bin/env python
"""
Job Creation Monitoring Script

This script monitors the progress of job creation and question generation.
Run this to check the status of all jobs in the system.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/home/nyuydine/Documents/UM/Umemployed')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umemployed.settings')
django.setup()

from job.models import Job, SkillQuestion
from asseessments.models import Question


def monitor_job_creation():
    """Monitor the status of job creation across all jobs."""
    
    print("=" * 60)
    print("JOB CREATION MONITORING REPORT")
    print("=" * 60)
    
    # Get all jobs
    jobs = Job.objects.all().order_by('-created_at')
    
    if not jobs.exists():
        print("No jobs found in the system.")
        return
    
    total_jobs = jobs.count()
    complete_jobs = jobs.filter(job_creation_is_complete=True).count()
    incomplete_jobs = total_jobs - complete_jobs
    
    print(f"Total Jobs: {total_jobs}")
    print(f"Complete Jobs: {complete_jobs}")
    print(f"Incomplete Jobs: {incomplete_jobs}")
    print(f"Completion Rate: {(complete_jobs/total_jobs)*100:.1f}%")
    print()
    
    print("DETAILED JOB STATUS:")
    print("-" * 60)
    
    for job in jobs[:10]:  # Show first 10 jobs
        skills_count = job.requirements.count()
        questions_count = SkillQuestion.objects.filter(job=job).count()
        skills_with_questions = SkillQuestion.objects.filter(
            job=job
        ).values('skill').distinct().count()
        
        status = "✅ COMPLETE" if job.job_creation_is_complete else "⏳ PENDING"
        
        print(f"Job ID: {job.id}")
        print(f"Title: {job.title}")
        print(f"Status: {status}")
        print(f"Skills Required: {skills_count}")
        print(f"Skills with Questions: {skills_with_questions}")
        print(f"Total Questions: {questions_count}")
        print(f"Created: {job.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        if skills_count > 0:
            progress = (skills_with_questions / skills_count) * 100
            print(f"Progress: {progress:.1f}%")
        
        print("-" * 40)
    
    if jobs.count() > 10:
        print(f"... and {jobs.count() - 10} more jobs")


def monitor_question_generation():
    """Monitor question generation statistics."""
    
    print("\n" + "=" * 60)
    print("QUESTION GENERATION STATISTICS")
    print("=" * 60)
    
    total_questions = SkillQuestion.objects.count()
    jobs_with_questions = SkillQuestion.objects.values('job').distinct().count()
    skills_with_questions = SkillQuestion.objects.values('skill').distinct().count()
    
    print(f"Total Questions Generated: {total_questions}")
    print(f"Jobs with Questions: {jobs_with_questions}")
    print(f"Skills with Questions: {skills_with_questions}")
    
    # Average questions per job
    if jobs_with_questions > 0:
        avg_questions = total_questions / jobs_with_questions
        print(f"Average Questions per Job: {avg_questions:.1f}")


def check_stuck_jobs():
    """Check for jobs that might be stuck in question generation."""
    
    print("\n" + "=" * 60)
    print("POTENTIALLY STUCK JOBS")
    print("=" * 60)
    
    import datetime
    from django.utils import timezone
    
    # Jobs created more than 1 hour ago but not complete
    one_hour_ago = timezone.now() - datetime.timedelta(hours=1)
    stuck_jobs = Job.objects.filter(
        created_at__lt=one_hour_ago,
        job_creation_is_complete=False,
        requirements__isnull=False
    ).distinct()
    
    if not stuck_jobs.exists():
        print("No stuck jobs found. ✅")
        return
    
    print(f"Found {stuck_jobs.count()} potentially stuck jobs:")
    print("-" * 40)
    
    for job in stuck_jobs:
        skills_count = job.requirements.count()
        questions_count = SkillQuestion.objects.filter(job=job).count()
        
        print(f"Job ID: {job.id}")
        print(f"Title: {job.title}")
        print(f"Created: {job.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"Skills: {skills_count}, Questions: {questions_count}")
        print("-" * 20)


if __name__ == "__main__":
    try:
        monitor_job_creation()
        monitor_question_generation()
        check_stuck_jobs()
        
        print("\n" + "=" * 60)
        print("Monitoring complete! 🎉")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error during monitoring: {e}")
        sys.exit(1)
