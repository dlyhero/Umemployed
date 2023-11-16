from django.db import models
from users.models import User

class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True , blank=True)
    logo = models.ImageField(upload_to="resume/images", blank=True, default="media/resume/images/PXL_20231104_141008232.MP.jpg")
    est_date = models.PositiveIntegerField(null=True , blank=True)
    city = models.CharField(max_length=50, null=True , blank=True)
    state = models.CharField(max_length=100, null=True , blank=True)

    def __str__(self):
        return self.name or ''