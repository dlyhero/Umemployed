# myapp/management/commands/populate_languages.py

import pycountry
from django.core.management.base import BaseCommand

from resume.models import Language


class Command(BaseCommand):
    help = "Populates the Language model with data from pycountry"

    def handle(self, *args, **kwargs):
        for lang in pycountry.languages:
            if hasattr(lang, "alpha_2"):
                Language.objects.get_or_create(name=lang.name)
        self.stdout.write(self.style.SUCCESS("Successfully populated languages"))
