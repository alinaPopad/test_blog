from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Post, Group, User
from .forms import PostForm, CommentForm

POST_FILTER = 10


@cache_page(20, key_prefix='index_page')
def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, POST_FILTER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, POST_FILTER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'group': group,
               'page_obj': page_obj,
               }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    count_posts = Post.objects.filter(author=author).count()
    profile_list = author.posts.select_related(
        'group', 'author')

    paginator = Paginator(profile_list, POST_FILTER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'author': author,
        'username': username,
        'count_posts': count_posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


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


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post_count = Post.objects.filter(author=post.author).count()
    title_post = post.text[:30]
    form = CommentForm()
    comments = post.comments.all()
    author = post.author
    context = {
        'post': post,
        'post_count': post_count,
        'title_post': title_post,
        'comments': comments,
        'form': form,
        'author': author,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None,)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('posts:profile', post.author)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {
        'is_edit': True,
        'form': form,
    }
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
        return render(request, 'posts/create_post.html', {'form': form})
    return render(request, 'posts/create_post.html', context)



