from django.core.management import setup_environ
from django.conf import settings
import os

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umemployed.settings")
setup_environ(settings)

import json
from resume.models import Skill, SkillCategory

def import_skills_data():
    with open('skills_data.json') as file:
        skills_data = json.load(file)

        for skill_data in skills_data:
            skill = Skill.objects.create(name=skill_data['bapi'])

            # Assuming skill categories are stored as a list of strings
            for key, value in skill_data.items():
                if value and key != 'bapi':
                    category, _ = SkillCategory.objects.get_or_create(name=value)
                    skill.categories.add(category)

            skill.save()

    print("Skills data imported successfully.")

if __name__ == "__main__":
    import_skills_data()