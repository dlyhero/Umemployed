import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import ApplicantAnswer, CompletedSkills, Skill

logger = logging.getLogger(__name__)

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import ApplicantAnswer, CompletedSkills, Skill


@receiver(post_save, sender=ApplicantAnswer)
def mark_skill_as_completed(sender, instance, created, **kwargs):
    if created:
        logger.debug(
            f"Signal triggered for ApplicantAnswer with ID: {instance.id} ================================="
        )

        application = instance.application
        skill = instance.question.skill

        logger.debug(
            f"Checking completion for skill_id: {skill.id} and job_id: {application.job.id}"
        )

        # Mark the skill as completed
        completed_skill, created = CompletedSkills.objects.get_or_create(
            user=application.user,
            job=application.job,
            skill=skill,
            defaults={"is_completed": True, "completed_at": timezone.now()},
        )

        if created:
            logger.debug(f"Completed skill created for skill_id: {skill.id}")
        else:
            completed_skill.is_completed = True
            completed_skill.completed_at = timezone.now()
            completed_skill.save()
            logger.debug(f"Completed skill updated for skill_id: {skill.id}")

        logger.debug(f"Completed skill processed for skill_id: {skill.id}")
