from django.contrib import admin

from .models import Comment, Follow, Like, Message, Post, UserProfile

# Register your models here.
admin.site.register(Post)
admin.site.register(Message)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Follow)
admin.site.register(UserProfile)
