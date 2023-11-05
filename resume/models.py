from django.db import models
from users.models import User

class Resume(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField( max_length=100, null=True , blank=True)
    surname = models.CharField( max_length=100,  null=True , blank=True)
    location = models.CharField( max_length=100,  null=True , blank=True)
    job_title = models.CharField(max_length=100,  null=True , blank=True)
    
    def __str__(self):
        first_name = self.first_name if self.first_name else ""
        surname = self.surname if self.surname else ""
        return first_name + " " + surname