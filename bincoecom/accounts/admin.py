from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'is_seller', 'is_seller_pending', 'created_at')
    list_filter = ('is_seller', 'is_seller_pending')
    search_fields = ('user__username', 'user__email', 'phone')
    list_editable = ('is_seller', 'is_seller_pending')
