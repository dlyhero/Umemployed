from django.core.management.base import BaseCommand
from django.db import transaction
from resume.models import Resume, SkillCategory


class Command(BaseCommand):
    help = "Sync job titles with categories for existing users"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='Sync only for specific user ID',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        user_id = options['user_id']
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))
        
        # Get resumes to process
        if user_id:
            resumes = Resume.objects.filter(user_id=user_id)
            self.stdout.write(f"Processing user ID: {user_id}")
        else:
            resumes = Resume.objects.all()
            self.stdout.write(f"Processing all {resumes.count()} resumes")
        
        updated_count = 0
        created_categories = 0
        errors = []
        
        for resume in resumes:
            try:
                if not resume.job_title:
                    self.stdout.write(f"⚠️  User {resume.user.id}: No job title found")
                    continue
                
                # Check if category is already set
                if resume.category and resume.category.name == resume.job_title:
                    self.stdout.write(f"✅ User {resume.user.id}: Category already correct ({resume.job_title})")
                    continue
                
                # Try to find existing category
                job_category = None
                
                # Exact match
                job_category = SkillCategory.objects.filter(name__iexact=resume.job_title).first()
                
                if not job_category:
                    # Partial match
                    job_category = SkillCategory.objects.filter(name__icontains=resume.job_title).first()
                
                if not job_category:
                    # Try variations
                    variations = [
                        resume.job_title,
                        resume.job_title.replace(' ', ''),
                        resume.job_title.lower(),
                        resume.job_title.title(),
                        resume.job_title.upper()
                    ]
                    for variation in variations:
                        job_category = SkillCategory.objects.filter(name__iexact=variation).first()
                        if job_category:
                            break
                
                if job_category:
                    if not dry_run:
                        with transaction.atomic():
                            resume.category = job_category
                            resume.save()
                    self.stdout.write(f"✅ User {resume.user.id}: Found category '{job_category.name}' for '{resume.job_title}'")
                else:
                    # Create new category
                    if not dry_run:
                        with transaction.atomic():
                            job_category, created = SkillCategory.objects.get_or_create(
                                name=resume.job_title,
                                defaults={'name': resume.job_title}
                            )
                            resume.category = job_category
                            resume.save()
                            if created:
                                created_categories += 1
                    else:
                        job_category = SkillCategory(name=resume.job_title)
                        created_categories += 1
                    
                    self.stdout.write(f"🆕 User {resume.user.id}: Created category '{job_category.name}' for '{resume.job_title}'")
                
                updated_count += 1
                
            except Exception as e:
                error_msg = f"❌ User {resume.user.id}: Error processing '{resume.job_title}': {str(e)}"
                self.stdout.write(self.style.ERROR(error_msg))
                errors.append(error_msg)
        
        # Summary
        self.stdout.write("\n" + "="*50)
        self.stdout.write("SYNC SUMMARY")
        self.stdout.write("="*50)
        self.stdout.write(f"Total resumes processed: {resumes.count()}")
        self.stdout.write(f"Resumes updated: {updated_count}")
        self.stdout.write(f"Categories created: {created_categories}")
        self.stdout.write(f"Errors: {len(errors)}")
        
        if errors:
            self.stdout.write("\nERRORS:")
            for error in errors:
                self.stdout.write(self.style.ERROR(f"  {error}"))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\nThis was a dry run. Run without --dry-run to apply changes."))
        else:
            self.stdout.write(self.style.SUCCESS("\nSync completed successfully!")) 