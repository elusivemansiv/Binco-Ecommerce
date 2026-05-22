from django.urls import path
from . import views

urlpatterns = [
    path('blog/', views.article_list, name='article_list'),
    path('blog/<slug:slug>/', views.article_detail, name='article_detail'),
    path('page/<slug:slug>/', views.page_detail, name='page_detail'),
]
