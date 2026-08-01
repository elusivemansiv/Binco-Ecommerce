from django.urls import path
from . import views

urlpatterns = [
    path('cms/sliders/', views.HomeSliderListView.as_view(), name='api_sliders'),
    path('cms/promotions/', views.PromotionCardListView.as_view(), name='api_promotions'),
    path('cms/banners/', views.BannerListView.as_view(), name='api_banners'),
    path('cms/articles/', views.ArticleListView.as_view(), name='api_articles'),
    path('cms/articles/<slug:slug>/', views.ArticleDetailView.as_view(), name='api_article_detail'),
    path('cms/pages/<slug:slug>/', views.StaticPageDetailView.as_view(), name='api_page_detail'),
    path('cms/about/', views.AboutPageView.as_view(), name='api_about'),
    path('cms/testimonials/', views.TestimonialListView.as_view(), name='api_testimonials'),
]
