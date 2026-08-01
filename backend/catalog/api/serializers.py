from rest_framework import serializers
from catalog.models import Product, Category, Color, Size, ProductVariation, ProductImage


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'code']


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'image', 'product_count']

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductVariationSerializer(serializers.ModelSerializer):
    color = ColorSerializer(read_only=True)
    size = SizeSerializer(read_only=True)

    class Meta:
        model = ProductVariation
        fields = ['id', 'color', 'size', 'stock']


class ProductImageSerializer(serializers.ModelSerializer):
    color = ColorSerializer(read_only=True)

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'color']


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listing pages."""
    category = serializers.SlugRelatedField(slug_field='name', read_only=True)
    category_slug = serializers.SlugRelatedField(source='category', slug_field='slug', read_only=True)
    discount_percent = serializers.ReadOnlyField()
    effective_price = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    total_stock = serializers.ReadOnlyField()
    seller_name = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'image', 'price', 'discount_price',
            'effective_price', 'discount_percent', 'average_rating',
            'total_stock', 'is_featured', 'category', 'category_slug',
            'seller_name', 'created_at',
        ]

    def get_seller_name(self, obj):
        if obj.seller:
            return obj.seller.get_full_name() or obj.seller.username
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full serializer for product detail page."""
    category = CategorySerializer(read_only=True)
    colors = ColorSerializer(many=True, read_only=True)
    sizes = SizeSerializer(many=True, read_only=True)
    variations = ProductVariationSerializer(many=True, read_only=True)
    extra_images = ProductImageSerializer(many=True, read_only=True)
    discount_percent = serializers.ReadOnlyField()
    effective_price = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    total_stock = serializers.ReadOnlyField()
    seller_name = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'image', 'price', 'discount_price',
            'effective_price', 'discount_percent', 'average_rating', 'review_count',
            'total_stock', 'stock', 'is_featured', 'is_active',
            'category', 'colors', 'sizes', 'variations', 'extra_images',
            'seller_name', 'created_at', 'updated_at',
        ]

    def get_seller_name(self, obj):
        if obj.seller:
            return obj.seller.get_full_name() or obj.seller.username
        return None

    def get_review_count(self, obj):
        return obj.reviews.count()
