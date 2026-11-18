import json
import datetime
import time
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import CreateArt
from .models import Article, Comment
from django.contrib import messages
import markdown2
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models import Q

# Create your views here.


def index(request):
    query = request.GET.get('q', '').strip()
    if query:
        multiQ = Q(title__icontains=query) | Q(desc__icontains=query)
        articles = Article.objects.filter(multiQ)
        search_message = f'"{query}"'
    else:
        articles = Article.objects.all()
        search_message = False

    return render(request, 'index.html', {
        'articles': articles,
        'search': search_message,
        'query': query,
    })


@login_required
def add(request):
    if request.method == "POST":
        form = CreateArt(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            article = Article(
                owner=request.user,
                title=data['title'],
                artImage=data['artImage'],
                content=data['content'],
                desc=data['desc'],
                category=data['category']
            )
            article.save()
            messages.success(request, 'Your dispatch has been published.')
            return HttpResponseRedirect(reverse('blog:index'))

        messages.error(request, 'Please correct the errors in the form.')
        return render(request, 'add.html', {
            'error': 'Please check the indicated fields below.',
            'form': form,  # Preserve user-entered data & validation errors
            'mode': 'Publish',
        })

    return render(request, 'add.html', {
        'form': CreateArt(),
        'mode': 'Publish',
    })


def categories(request):
    # Retrieve category keys from Article choice definitions
    all_articles = Article.objects.all()
    category_counts = {}
    for choice_val, choice_label in Article.categoryList:
        category_counts[choice_val] = {
            'slug': choice_val,
            'label': choice_label,
            'count': 0
        }
    for art in all_articles:
        for cat in art.category:
            if cat in category_counts:
                category_counts[cat]['count'] += 1

    return render(request, 'categories.html', {
        'category_stats': list(category_counts.values())
    })


def singleArt(request, id):
    try:
        art = Article.objects.get(pk=id)
    except Article.DoesNotExist:
        return render(request, '404.html', status=404)

    comments = Comment.objects.filter(article=art).all()
    rendered_content = markdown2.markdown(
        art.content,
        extras=["fenced-code-blocks", "tables", "header-ids", "strike", "code-friendly"]
    )
    return render(request, 'singleArt.html', {
        'post': art,
        'content': rendered_content,
        'comments': comments,
    })


# handle 404
def error404(request, exception=None):
    return render(request, '404.html', status=404)


@login_required
@csrf_exempt
def save(request, id):
    if request.method == "POST":
        try:
            getArticle = Article.objects.get(pk=id)
        except Article.DoesNotExist:
            return JsonResponse({"error": "Not found"}, status=404)

        if request.user in getArticle.bookmarks.all():
            getArticle.bookmarks.remove(request.user)
            return JsonResponse({"message": "removed", "saved": False})
        else:
            getArticle.bookmarks.add(request.user)
            return JsonResponse({"message": "added", "saved": True})
    return JsonResponse({"error": "Method not allowed"}, status=405)


@login_required
def bookmarks(request):
    marked_posts = Article.objects.filter(bookmarks=request.user).all()
    return render(request, 'bookmarks.html', {
        'postsMarked': marked_posts,
    })


def category(request, name):
    targetArticles = []
    allArticles = Article.objects.all()
    for art in allArticles:
        for cat in art.category:
            if cat.lower() == name.lower():
                targetArticles.append(art)
                break

    # Get readable label
    label_dict = dict(Article.categoryList)
    readable_label = label_dict.get(name, name.title())

    return render(request, 'category.html', {
        'title': readable_label,
        'raw_title': name,
        'targetArticle': targetArticles,
    })


@login_required
@csrf_exempt
def voting(request, id):
    try:
        targetArticle = Article.objects.get(pk=id)
    except Article.DoesNotExist:
        return JsonResponse({'error': 'Article not found'}, status=404)

    if request.method == "PUT":
        if request.user in targetArticle.upvote.all():
            targetArticle.upvote.remove(request.user)
            return JsonResponse({
                'messege': 'downvote',
                'message': 'downvote',
                'voted': False,
                'count': targetArticle.upvote.count()
            })
        else:
            targetArticle.upvote.add(request.user)
            return JsonResponse({
                'messege': 'upvote',
                'message': 'upvote',
                'voted': True,
                'count': targetArticle.upvote.count()
            })
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
@csrf_exempt
def delete(request, id):
    try:
        targetArticle = Article.objects.get(pk=id)
    except Article.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    if targetArticle.owner == request.user:
        if request.method == "POST":
            targetArticle.delete()
            return JsonResponse({'message': 'deleted'})
    return JsonResponse({'error': 'Forbidden'}, status=403)


@login_required
def update(request, id):
    try:
        targetArticle = Article.objects.get(pk=id)
    except Article.DoesNotExist:
        return render(request, '404.html', status=404)

    if targetArticle.owner != request.user:
        messages.error(request, 'You do not have permission to edit this dispatch.')
        return HttpResponseRedirect(reverse('blog:index'))

    if request.method == "POST":
        form = CreateArt(request.POST, request.FILES, instance=targetArticle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Article updated successfully.')
            return HttpResponseRedirect(reverse('blog:singleArt', kwargs={'id': id}))
        else:
            messages.error(request, 'Please check the indicated errors.')
            return render(request, 'add.html', {
                'form': form,
                'mode': 'Update',
            })

    form = CreateArt(instance=targetArticle)
    return render(request, 'add.html', {
        'form': form,
        'mode': 'Update',
    })


@login_required
@csrf_exempt
def addComment(request, id):
    if request.method == "POST":
        try:
            targetArticle = Article.objects.get(pk=id)
        except Article.DoesNotExist:
            return JsonResponse({'error': 'Article not found'}, status=404)

        try:
            data = json.loads(request.body)
            content = data.get('comment', '').strip()
        except Exception:
            content = ''

        if not content:
            return JsonResponse({'error': 'Empty comment'}, status=400)

        newComment = Comment(
            owner=request.user,
            article=targetArticle,
            content=content
        )
        newComment.save()

        # Format date nicely
        formatted_date = newComment.created.strftime("%b %d, %Y · %I:%M %p")

        return JsonResponse({
            'content': newComment.content,
            'owner': request.user.username,
            'created': formatted_date,
            'numbComments': Comment.objects.filter(article=targetArticle).count()
        })

    return HttpResponseRedirect(reverse('blog:singleArt', kwargs={'id': id}))
