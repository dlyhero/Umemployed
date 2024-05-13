from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, Message, Like, Comment, Follow
from .forms import PostForm, MessageForm
from users.models import User

@login_required
def create_post(request):
    """
    View for creating a new post.

    Allows authenticated users to create a new post with text and optional image.
    """
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('/')  
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})

@login_required
def view_post(request, post_id):
    """
    View for viewing a single post.

    Allows authenticated users to view a single post.
    """
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'posts/view_post.html', {'post': post})

@login_required
def edit_post(request, post_id):
    """
    View for editing an existing post.

    Allows authenticated users to edit their own posts.
    """
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('/') 
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, post_id):
    """
    View for deleting a post.

    Allows authenticated users to delete their own posts.
    """
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('/')  
    return render(request, 'posts/delete_post.html', {'post': post})

@login_required
def send_message(request, recipient_id):
    """
    View for sending a message to another user.

    Allows authenticated users to send messages to other users.
    """
    recipient = get_object_or_404(User, id=recipient_id)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.save()
            return redirect('inbox')  
    else:
        form = MessageForm()
    return render(request, 'posts/send_message.html', {'form': form, 'recipient': recipient})

@login_required
def view_message(request, message_id):
    """
    View for viewing a single message.

    Allows authenticated users to view a single message and mark it as read.
    """
    message = get_object_or_404(Message, id=message_id)
    if not message.is_read:
        message.is_read = True
        message.save()
    return render(request, 'posts/view_message.html', {'message': message})

@login_required
def delete_message(request, message_id):
    """
    View for deleting a message.

    Allows authenticated users to delete their own messages.
    """
    message = get_object_or_404(Message, id=message_id)
    if request.method == 'POST':
        message.delete()
        return redirect('inbox')  
    return render(request, 'posts/delete_message.html', {'message': message})

@login_required
def inbox(request):
    """
    View for displaying the user's inbox.

    Allows authenticated users to view their received messages.
    """
    messages = Message.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'posts/inbox.html', {'messages': messages})

@login_required
def like_post(request, post_id):
    """
    View for liking a post.

    Allows authenticated users to like a post.
    """
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
    return redirect('view_post', post_id=post_id)

@login_required
def comment_post(request, post_id):
    """
    View for commenting on a post.

    Allows authenticated users to comment on a post.
    """
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            comment = Comment.objects.create(user=request.user, post=post, content=content)
    return redirect('view_post', post_id=post_id)

@login_required
def follow_user(request, user_id):
    """
    View for following a user.

    Allows authenticated users to follow another user.
    """
    user_to_follow = get_object_or_404(User, id=user_id)
    follow, created = Follow.objects.get_or_create(follower=request.user, followed=user_to_follow)
    if not created:
        follow.delete()
    return redirect('view_post', post_id=post_id)
