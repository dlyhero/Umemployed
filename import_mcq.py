import os
import django
import sqlite3

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umemployed.settings")

# Initialize Django
django.setup()

# Now you can import your Django models
from job.models import MCQ

def import_data_to_django():
    # Connect to SQLite database
    conn = sqlite3.connect("/home/nyuydinebill/Desktop/Umemployed/SkillExtracter/app/skills_db.db")  # Replace with actual path
    cursor = conn.cursor()

    # Retrieve data from SQLite database
    cursor.execute("SELECT * FROM mcqs")
    mcqs = cursor.fetchall()

    # Import data into Django model
    for mcq_data in mcqs:
        mcq_instance = MCQ.objects.create(
            job_title=mcq_data[0],
            question=mcq_data[1],
            option_a=mcq_data[2],
            option_b=mcq_data[3],
            option_c=mcq_data[4],
            option_d=mcq_data[5],
            correct_answer=mcq_data[6],
        )
        mcq_instance.save()

    # Close SQLite connection
    conn.close()

# Call the import function
import_data_to_django()
