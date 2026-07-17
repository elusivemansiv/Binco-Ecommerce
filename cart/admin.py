from django.contrib import admin
from .models import Cart, CartItem, Coupon

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    inlines = [CartItemInline]

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'valid_from', 'valid_to', 'is_active', 'used_count', 'max_uses')
    list_editable = ('is_active',)
