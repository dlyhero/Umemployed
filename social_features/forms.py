from django import forms
from .models import Post, Message

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = '__all__'