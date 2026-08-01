from rest_framework import serializers
from cms.models import (
    HomeSlider, PromotionCard, Banner, Article, StaticPage,
    AboutPage, AboutStat, AboutService, AboutTeamMember, Testimonial,
)


class HomeSliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeSlider
        fields = ['id', 'title', 'subtitle', 'image', 'link_url', 'order']


class PromotionCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionCard
        fields = ['id', 'title', 'subtitle', 'image', 'link_url', 'badge_text', 'order']


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'title', 'subtitle', 'image', 'link_url', 'button_text', 'order']


class ArticleListSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'category', 'image', 'author_name',
                  'is_published', 'published_at']

    def get_author_name(self, obj):
        if obj.author:
            return obj.author.get_full_name() or obj.author.username
        return None


class ArticleDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'category', 'image', 'content',
                  'author_name', 'published_at', 'updated_at']

    def get_author_name(self, obj):
        if obj.author:
            return obj.author.get_full_name() or obj.author.username
        return None


class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = ['id', 'title', 'slug', 'content']


class AboutStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutStat
        fields = ['value', 'label', 'order']


class AboutServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutService
        fields = ['icon_class', 'title', 'description', 'order']


class AboutTeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutTeamMember
        fields = ['name', 'role', 'image', 'facebook_url', 'twitter_url',
                  'instagram_url', 'linkedin_url', 'order']


class AboutPageSerializer(serializers.ModelSerializer):
    stats = AboutStatSerializer(many=True, read_only=True)
    services = AboutServiceSerializer(many=True, read_only=True)
    team_members = AboutTeamMemberSerializer(many=True, read_only=True)

    class Meta:
        model = AboutPage
        fields = [
            'hero_title', 'mission_text', 'vision_text', 'hero_image_1', 'hero_image_2',
            'services_title', 'services_subtitle',
            'feature1_tagline', 'feature1_title', 'feature1_description',
            'feature1_bullet1', 'feature1_bullet2', 'feature1_bullet3',
            'feature1_image1', 'feature1_image2',
            'app_section_title', 'app_section_description', 'app_image_1', 'app_image_2',
            'play_store_link', 'app_store_link',
            'feature2_tagline', 'feature2_title', 'feature2_description',
            'feature2_bullet1', 'feature2_bullet2', 'feature2_bullet3',
            'feature2_image', 'feature2_youtube_link',
            'team_title', 'team_subtitle',
            'stats', 'services', 'team_members',
        ]


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['id', 'customer_name', 'customer_role', 'review_text', 'created_at']
