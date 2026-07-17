from django.urls import path
from . import views

urlpatterns = [
    path('blog/', views.article_list, name='article_list'),
    path('blog/<slug:slug>/', views.article_detail, name='article_detail'),
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('page/<slug:slug>/', views.page_detail, name='page_detail'),
]
