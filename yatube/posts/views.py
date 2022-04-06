from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CommentForm, PostForm
from yatube.settings import PAGINATOR_ITEMS_ON_PAGE
from .forms import PostForm
from .models import Group, Post, User, Follow


LIMIT_POST = 10


def index(request):
    posts_list = Post.objects.all()
    paginator = Paginator(posts_list, LIMIT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    paginator = Paginator(posts_list, LIMIT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(
        request,
        'posts/group_list.html',
        context
    )


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    group = post.group
    author = post.author
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'group': group,
        'author': author,
        'form': form,
        'comments': comments,
    }
    return render(
        request,
        'posts/post_detail.html',
        context
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_list = author.posts.all()
    paginator = Paginator(author_list, LIMIT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = request.user.is_authenticated and author.following.filter(user=request.user).exists()
    context = {
        'author': author,
        'page_obj': page_obj,
        'author_list': author_list,
        'following': following,
    }
    return render(
        request,
        'posts/profile.html',
        context
    )


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)
    return render(request, 'posts/create_edit_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.id)
    return render(
        request,
        'posts/create_edit_post.html',
        {'form': form, 'is_edit': True, 'post_id': post.id},
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    follow = True
    paginator = Paginator(post_list, LIMIT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'follow': follow
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("posts:profile", username=username)