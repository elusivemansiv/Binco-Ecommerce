from django.contrib import admin
from .models import Banner, Article, StaticPage, HomeSlider, PromotionCard, Testimonial


@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'subtitle')


@admin.register(PromotionCard)
class PromotionCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'subtitle')


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'subtitle')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'is_published', 'published_at')
    list_filter = ('category', 'is_published', 'author')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}

from .models import AboutPage, AboutStat, AboutService, AboutTeamMember

class AboutStatInline(admin.TabularInline):
    model = AboutStat
    extra = 1

class AboutServiceInline(admin.StackedInline):
    model = AboutService
    extra = 1

class AboutTeamMemberInline(admin.StackedInline):
    model = AboutTeamMember
    extra = 1

@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    inlines = [AboutStatInline, AboutServiceInline, AboutTeamMemberInline]

    def has_add_permission(self, request):
        if AboutPage.objects.exists():
            return False
        return True

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_role', 'image', 'is_active', 'created_at')
    list_editable = ('is_active',)
    search_fields = ('customer_name', 'customer_role', 'review_text')
