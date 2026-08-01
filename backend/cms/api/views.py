from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from cms.models import HomeSlider, PromotionCard, Banner, Article, StaticPage, AboutPage, Testimonial
from .serializers import (
    HomeSliderSerializer, PromotionCardSerializer, BannerSerializer,
    ArticleListSerializer, ArticleDetailSerializer, StaticPageSerializer,
    AboutPageSerializer, TestimonialSerializer,
)


class HomeSliderListView(generics.ListAPIView):
    queryset = HomeSlider.objects.filter(is_active=True)
    serializer_class = HomeSliderSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class PromotionCardListView(generics.ListAPIView):
    queryset = PromotionCard.objects.filter(is_active=True)
    serializer_class = PromotionCardSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class BannerListView(generics.ListAPIView):
    queryset = Banner.objects.filter(is_active=True)
    serializer_class = BannerSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class ArticleListView(generics.ListAPIView):
    queryset = Article.objects.filter(is_published=True)
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.AllowAny]


class ArticleDetailView(generics.RetrieveAPIView):
    queryset = Article.objects.filter(is_published=True)
    serializer_class = ArticleDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class StaticPageDetailView(generics.RetrieveAPIView):
    queryset = StaticPage.objects.filter(is_active=True)
    serializer_class = StaticPageSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class AboutPageView(generics.RetrieveAPIView):
    serializer_class = AboutPageSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return AboutPage.objects.first()


class TestimonialListView(generics.ListAPIView):
    queryset = Testimonial.objects.filter(is_active=True)
    serializer_class = TestimonialSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
