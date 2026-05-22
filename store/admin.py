from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Product, ProductImage, ProductReview,
    Cart, CartItem, Coupon, Order, OrderItem, Wishlist,
    Color, Size, ProductVariation,
    ShippingConfig
)





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
    list_display = ('image_tag', 'name', 'seller', 'category', 'price', 'discount_price', 'total_stock', 'is_featured', 'is_active', 'created_at')
    list_display_links = ('image_tag', 'name')
    list_filter = ('is_featured', 'is_active', 'category')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariationInline]
    readonly_fields = ('stock', 'total_stock')
    list_editable = ('is_featured', 'is_active')
    filter_horizontal = ('colors', 'sizes')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height: 45px; border-radius: 5px; object-fit: cover; box-shadow: 0 2px 5px rgba(0,0,0,0.1);" />', obj.image.url)
        return "-"
    image_tag.short_description = 'Image'


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
    readonly_fields = ('image_tag', 'subtotal')
    fields = ('image_tag', 'product', 'product_name', 'price', 'quantity', 'color', 'size', 'subtotal')

    def image_tag(self, obj):
        if obj.selected_image:
            return format_html('<img src="{}" style="width: 45px; height: 45px; border-radius: 5px; object-fit: cover; box-shadow: 0 2px 5px rgba(0,0,0,0.1);" />', obj.selected_image.url)
        return "-"
    image_tag.short_description = 'Image'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_tag', 'user', 'full_name', 'total_price', 'discount_amount', 'status', 'payment_method', 'created_at')
    list_display_links = ('id', 'image_tag', 'user')
    list_filter = ('status', 'payment_method')
    search_fields = ('user__username', 'full_name', 'email')
    list_editable = ('status',)
    inlines = [OrderItemInline]
    actions = ['download_invoice']

    def download_invoice(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one order to download the invoice.", level='warning')
            return
        order = queryset.first()
        from django.shortcuts import redirect
        return redirect('generate_invoice', order_id=order.id)
    
    download_invoice.short_description = "Download PDF Invoice"

    def image_tag(self, obj):
        first_item = obj.items.first()
        if first_item and first_item.selected_image:
            img_url = first_item.selected_image.url
            extra_text = ""
            if obj.items.count() > 1:
                extra_text = f" +{obj.items.count() - 1}"
            
            return format_html(
                '<div style="display:flex; align-items:center; gap:8px;">'
                '<img src="{}" style="width: 45px; height: 45px; border-radius: 5px; object-fit: cover; box-shadow: 0 2px 5px rgba(0,0,0,0.1);" title="{}" />'
                '<span style="font-size: 11px; color: #666; font-weight: bold;">{}</span>'
                '</div>',
                img_url, first_item.product_name, extra_text
            )
        return "-"
    image_tag.short_description = 'Items'


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
