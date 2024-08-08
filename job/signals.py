# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import ApplicantAnswer, Application

# @receiver(post_save, sender=ApplicantAnswer)
# def update_application_quiz_score(sender, instance, **kwargs):
#     try:
#         application = instance.application
#         print(f"Updating quiz score for application: {application.id}")
        
#         # Filter answers related to the application
#         answers = ApplicantAnswer.objects.filter(application=application)
        
#         # Calculate the total quiz score
#         total_score = sum(answer.score for answer in answers)
#         print(f"Total score calculated: {total_score}")
        
#         # Update the application with the total score
#         application.quiz_score = total_score
#         application.save()
#         print(f"Application saved: {application}")
#     except Exception as e:
#         print(f"Unexpected error: {e}")
