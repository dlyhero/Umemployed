from umemployed.celery import shared_task
import sqlite3
from django.db import transaction
from .umemployed.celery import app
from resume.models import Skill, SkillCategory

@shared_task
def import_skills_data():
    # Connect to the SQLite database
    fastapi_db_conn = sqlite3.connect('/home/nyuydinebill/Desktop/Umemployed/UmEmployed API/Skills_ChatGPT/app/skills_db.db')

    # Query the skills data
    cursor = fastapi_db_conn.cursor()
    cursor.execute("SELECT title, skills FROM jobs")

    with transaction.atomic():  # Ensure atomicity of the transaction
        for job_row in cursor.fetchall():
            job_title, skills = job_row
            skills_list = [skill.strip() for skill in skills.split(',')]  # Split skills string by commas

            # Create SkillCategory for the job title
            skill_category, created = SkillCategory.objects.get_or_create(name=job_title)

            # Iterate over skills list and create Skill objects
            for skill_description in skills_list:
                if skill_description:  # Skip empty strings
                    # Create or get the skill and associate it with the SkillCategory
                    skill, created = Skill.objects.get_or_create(name=skill_description)
                    skill.categories.add(skill_category)
                    skill.save()

    print("Skills data imported successfully.")

# Run this task periodically using Celery beat scheduler
# For example, to run every hour, add the following to your settings.py:
# CELERY_BEAT_SCHEDULE = {
#     'import_skills_data_task': {
#         'task': 'path.to.import_skills_data',
#         'schedule': timedelta(hours=1),
#     },
# }
