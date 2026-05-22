from django.shortcuts import render, get_object_or_404
from .models import Article, StaticPage

def article_list(request):
    articles = Article.objects.filter(is_published=True)
    return render(request, 'cms/article_list.html', {'articles': articles})

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    return render(request, 'cms/article_detail.html', {'article': article})

def page_detail(request, slug):
    page = get_object_or_404(StaticPage, slug=slug, is_active=True)
    return render(request, 'cms/page_detail.html', {'page': page})
