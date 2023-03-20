from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from hitcount.views import HitCountDetailView
from taggit.models import Tag

from blog.forms import PostCreateForm, CommentForm, SearchForm
from blog.models import Post, Comment, CommentContact


def post_list(request, tag_slug=None):
    posts = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__in=[tag])

    paginator = Paginator(posts, 4)
    page_num = request.GET.get('page')
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
            return HttpResponse('')
    return render(request, 'blog/post/list.html', {'tag': tag, 'page_obj': page_obj})


class PostDetailView(HitCountDetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    count_hit = True


@login_required
def post_create(request):
    if request.method == 'POST':
        post_form = PostCreateForm(request.POST)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.slug = slugify(post.title)
            post.author = request.user
            post.save()
            tags_list = request.POST['tags']
            post.tags.add(tags_list)
            messages.success(request, 'Your post has been saved and will be published after confirmation ')

            return render(request, 'blog/detail.html', {'post': post})
    else:
        post_form = PostCreateForm()
    return render(request, 'blog/create.html', {'post_form': post_form})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.published.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)
                                              ).filter(rank__gte=0.3).order_by('-rank')

    return render(request, 'blog/search.html', {'form': form, 'query': query, 'results': results})


@require_POST
@login_required
def post_like(request):
    post_id = request.POST.get('id')
    action = request.POST.get('action')
    if post_id and action:
        post = get_object_or_404(Post, id=post_id)
        if action == 'like':
            post.users_like.add(request.user)
        else:
            post.users_like.remove(request.user)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'})


@login_required
def comment_comment(request, post_id, comment_id):
    comment_from = get_object_or_404(Comment, id=comment_id, active=True)
    post = get_object_or_404(Post, id=post_id)
    now_commented = False
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment_to = comment_form.save(commit=False)
            comment_to.post = post
            comment_to.user = request.user
            comment_to.save()
            CommentContact.objects.get_or_create(comment_from=comment_from, comment_to=comment_to)
            now_commented = True
    else:
        comment_form = CommentForm()

    return render(request, 'blog/comment.html', {'comment_form': comment_form, 'now_commented': now_commented})





