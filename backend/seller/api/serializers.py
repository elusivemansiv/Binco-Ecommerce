from rest_framework import serializers
from catalog.models import Product, Category, Color, Size, ProductVariation, ProductImage
from orders.models import OrderItem
from catalog.api.serializers import ColorSerializer, SizeSerializer


class SellerProductSerializer(serializers.ModelSerializer):
    """Serializer for seller's product CRUD operations."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    total_stock = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category', 'category_name',
            'price', 'discount_price', 'image', 'stock', 'total_stock',
            'is_featured', 'is_active', 'average_rating', 'created_at',
        ]
        read_only_fields = ['id', 'slug', 'total_stock', 'average_rating', 'created_at']


class SellerProductCreateSerializer(serializers.ModelSerializer):
    """Create/Update serializer with writable category and color/size ids."""
    colors = serializers.PrimaryKeyRelatedField(
        queryset=Color.objects.all(), many=True, required=False
    )
    sizes = serializers.PrimaryKeyRelatedField(
        queryset=Size.objects.all(), many=True, required=False
    )

    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'price', 'discount_price',
            'image', 'stock', 'is_active', 'colors', 'sizes',
        ]


class SellerVariationSerializer(serializers.ModelSerializer):
    color = ColorSerializer(read_only=True)
    size = SizeSerializer(read_only=True)
    color_id = serializers.PrimaryKeyRelatedField(
        queryset=Color.objects.all(), source='color', write_only=True, required=False, allow_null=True
    )
    size_id = serializers.PrimaryKeyRelatedField(
        queryset=Size.objects.all(), source='size', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = ProductVariation
        fields = ['id', 'color', 'size', 'color_id', 'size_id', 'stock']
        read_only_fields = ['id']


class SellerProductImageSerializer(serializers.ModelSerializer):
    color_id = serializers.PrimaryKeyRelatedField(
        queryset=Color.objects.all(), source='color', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'color', 'color_id']
        read_only_fields = ['id', 'color']


class SellerOrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'price', 'quantity', 'color', 'size', 'subtotal']


class SellerOrderSerializer(serializers.Serializer):
    """Custom serializer grouping order items by order for a seller."""
    order_id = serializers.IntegerField()
    customer_name = serializers.CharField()
    status = serializers.CharField()
    status_display = serializers.CharField()
    payment_method = serializers.CharField()
    created_at = serializers.DateTimeField()
    seller_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    items = SellerOrderItemSerializer(many=True)


class UpdateOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['pending', 'processing', 'cancelled', 'return_approved'])

