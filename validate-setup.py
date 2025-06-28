#!/usr/bin/env python3
"""
Validation script to check if the async resume enhancement setup is complete.
Run this before deploying to production.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report status."""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (NOT FOUND)")
        return False

def check_docker_file_content(filepath, required_patterns):
    """Check if Dockerfile contains required patterns."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            for pattern in required_patterns:
                if pattern in content:
                    print(f"✅ Dockerfile contains: {pattern}")
                else:
                    print(f"❌ Dockerfile missing: {pattern}")
                    return False
        return True
    except FileNotFoundError:
        print(f"❌ Dockerfile not found: {filepath}")
        return False

def check_workflow_file():
    """Check if GitHub Actions workflow is properly configured."""
    workflow_file = ".github/workflows/deploy-celery-worker.yml"
    if not Path(workflow_file).exists():
        print(f"❌ Workflow file not found: {workflow_file}")
        return False
    
    with open(workflow_file, 'r') as f:
        content = f.read()
        
    required_elements = [
        "umemployed/um_celery_worker",
        "DOCKER_HUB_CELERY_USERNAME",
        "DOCKER_HUB_CELERY_TOKEN",
        "docker/build-push-action@v4"
    ]
    
    for element in required_elements:
        if element in content:
            print(f"✅ Workflow contains: {element}")
        else:
            print(f"❌ Workflow missing: {element}")
            return False
    
    return True

def check_celery_tasks():
    """Check if Celery tasks are properly defined."""
    task_files = [
        "resume/tasks.py",
        "job/tasks.py",
        "users/tasks.py",
        "messaging/tasks.py"
    ]
    
    found_tasks = 0
    for task_file in task_files:
        if Path(task_file).exists():
            with open(task_file, 'r') as f:
                content = f.read()
                if "@shared_task" in content or "@task" in content:
                    print(f"✅ Tasks found in: {task_file}")
                    found_tasks += 1
                else:
                    print(f"⚠️  No tasks found in: {task_file}")
        else:
            print(f"⚠️  Task file not found: {task_file}")
    
    return found_tasks > 0

def main():
    print("🔍 Validating Async Resume Enhancement Setup")
    print("=" * 50)
    
    all_good = True
    
    # Check core files
    print("\n📁 Checking Core Files:")
    files_to_check = [
        ("Dockerfile.celery", "Celery Dockerfile"),
        ("entrypoint.sh", "Container entrypoint script"),
        ("requirements.txt", "Python requirements"),
        ("umemployed/celery.py", "Celery configuration"),
        ("resume/api/views.py", "Resume API views"),
        ("resume/models.py", "Resume models"),
    ]
    
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_good = False
    
    # Check Dockerfile content
    print("\n🐳 Checking Dockerfile.celery:")
    dockerfile_patterns = [
        "FROM python:3.10-slim",
        "COPY requirements.txt",
        "RUN pip install",
        "CMD [\"celery\", \"-A\", \"umemployed\", \"worker\""
    ]
    if not check_docker_file_content("Dockerfile.celery", dockerfile_patterns):
        all_good = False
    
    # Check workflow
    print("\n⚙️  Checking GitHub Actions Workflow:")
    if not check_workflow_file():
        all_good = False
    
    # Check Celery tasks
    print("\n🔄 Checking Celery Tasks:")
    if not check_celery_tasks():
        all_good = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 All checks passed! Your setup is ready for deployment.")
        print("\n📝 Next steps:")
        print("1. Set up GitHub secrets (DOCKER_HUB_CELERY_USERNAME, DOCKER_HUB_CELERY_TOKEN)")
        print("2. Push to main branch to trigger deployment")
        print("3. Update Azure Container Instance with new image")
        print("4. Test the async resume enhancement API")
    else:
        print("❌ Some issues were found. Please fix them before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()
