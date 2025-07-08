from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class StartChatForm(forms.Form):
    recipient = forms.ModelChoiceField(
        queryset=User.objects.all(), label="Select user to chat with"
    )
