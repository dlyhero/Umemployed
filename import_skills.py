import os
import sqlite3
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umemployed.settings")
django.setup()

from resume.models import Skill, SkillCategory

def import_skills_data():
    # Connect to the FastAPI SQLite database
    fastapi_db_conn = sqlite3.connect('/home/nyuydinebill/Desktop/Umemployed/UmEmployed API/Skills_ChatGPT/app/skills_db.db')

    # Query the skills data from the FastAPI database
    cursor = fastapi_db_conn.cursor()
    cursor.execute("SELECT title, skills FROM jobs")

    for job_row in cursor.fetchall():
        job_title, skills = job_row
        # Convert skills from a comma-separated string to a list of strings
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

if __name__ == "__main__":
    import_skills_data()
