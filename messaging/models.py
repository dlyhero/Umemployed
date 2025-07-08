from django.conf import settings
from django.db import models


class Conversation(models.Model):
    participant1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="participant1_conversations",
        on_delete=models.CASCADE,
    )
    participant2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="participant2_conversations",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.participant1} - {self.participant2}"


class ChatMessage(models.Model):
    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="sender", on_delete=models.CASCADE
    )
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"


class MessageReaction(models.Model):
    message = models.ForeignKey(ChatMessage, related_name="reactions", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=50)  # e.g., 'like', 'love', 'laugh', etc.

    class Meta:
        unique_together = ("message", "user", "reaction")

    def __str__(self):
        return f"{self.user} reacted with {self.reaction} to message {self.message.id}"
