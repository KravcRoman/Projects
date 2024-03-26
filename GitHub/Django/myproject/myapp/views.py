# blog/views.py
from django.shortcuts import render, redirect
from .models import Article, Comment
from .forms import ArticleForm, CommentForm
from django.contrib.auth.decorators import login_required

def article_list(request):
    articles = Article.objects.all()
    return render(request, 'article_detail.html', {'articles': articles})

@login_required
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('article_list')
    else:
        form = ArticleForm()
    return render(request, 'create_article.html', {'form': form})

def article_detail(request, pk):
    article = Article.objects.get(pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.save()
            return redirect('article_detail', pk=pk)
    else:
        form = CommentForm()
    return render(request, 'article_detail.html', {'article': article, 'form': form})




