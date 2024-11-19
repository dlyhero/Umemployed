from django.db import models
from users.models import User

# Create your models here.
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    text = models.TextField(null = True)
    image = models.ImageField(null=True, upload_to='image/messages')
    video = models.FileField(null=True, blank=True, upload_to='video/messages')
    created = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    idd = models.PositiveIntegerField(default = 0)
    replyTo = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_DEFAULT, default=None, related_name='replies' )
    class Meta:
        ordering = ['created']

    @staticmethod
    def getRoomName(user1, user2):
        return f'{min(user1.id, user2.id)}_{max(user1.id,user2.id)}'
        

    def __str__(self):
        return f'from {self.sender.username} to {self.receiver.username} at {self.created}'
