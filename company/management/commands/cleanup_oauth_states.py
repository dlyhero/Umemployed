"""
Management command to clean up expired OAuth states
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from company.models import OAuthState


class Command(BaseCommand):
    help = 'Clean up expired OAuth states (older than 1 hour)'

    def handle(self, *args, **options):
        cutoff_time = timezone.now() - timedelta(hours=1)
        expired_states = OAuthState.objects.filter(created_at__lt=cutoff_time)
        count = expired_states.count()
        
        if count > 0:
            expired_states.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {count} expired OAuth states')
            )
        else:
            self.stdout.write('No expired OAuth states found')
