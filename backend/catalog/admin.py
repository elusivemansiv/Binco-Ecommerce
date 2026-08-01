from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, Color, Size, ProductVariation

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
