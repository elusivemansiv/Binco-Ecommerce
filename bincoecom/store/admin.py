from django.contrib import admin
from .models import (
    Category, Product, ProductImage, ProductReview,
    Cart, CartItem, Coupon, Order, OrderItem, Wishlist,
    Color, Size, ProductVariation, HomeSlider, PromotionCard,
    ShippingConfig
)


@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')


@admin.register(PromotionCard)
class PromotionCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'category', 'price', 'discount_price', 'total_stock', 'is_featured', 'is_active', 'created_at')
    list_filter = ('is_featured', 'is_active', 'category')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariationInline]
    readonly_fields = ('stock', 'total_stock')
    list_editable = ('is_featured', 'is_active')
    filter_horizontal = ('colors', 'sizes')


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    list_filter = ('rating',)


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


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'total_price', 'discount_amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('user__username', 'full_name', 'email')
    list_editable = ('status',)
    inlines = [OrderItemInline]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user',)
    filter_horizontal = ('products',)


@admin.register(ShippingConfig)
class ShippingConfigAdmin(admin.ModelAdmin):
    list_display = ('shipping_charge', 'free_shipping_threshold', 'is_active', 'updated_at')
    
    def has_add_permission(self, request):
        # Prevent adding more than one config
        return not ShippingConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting the config
        return False
