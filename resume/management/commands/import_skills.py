from django.core.management.base import BaseCommand
import json
from resume.models import Skill, SkillCategory

class Command(BaseCommand):
    help = 'Import skills data'

    def handle(self, *args, **options):
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

        self.stdout.write(self.style.SUCCESS('Skills data imported successfully.'))