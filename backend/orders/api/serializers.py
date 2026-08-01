from rest_framework import serializers
from orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()
    selected_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'price', 'quantity',
                  'color', 'size', 'subtotal', 'selected_image']

    def get_selected_image(self, obj):
        img = obj.selected_image
        if img:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(img.url)
            return img.url
        return None


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight order list serializer."""
    items_count = serializers.SerializerMethodField()
    final_total = serializers.ReadOnlyField(source='get_final_total')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'status_display', 'payment_method', 'payment_method_display',
            'total_price', 'discount_amount', 'shipping_charge', 'final_total',
            'items_count', 'created_at',
        ]

    def get_items_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """Full order detail serializer."""
    items = OrderItemSerializer(many=True, read_only=True)
    final_total = serializers.ReadOnlyField(source='get_final_total')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'full_name', 'email', 'phone', 'address', 'city', 'postal_code',
            'status', 'status_display', 'payment_method', 'payment_method_display',
            'total_price', 'discount_amount', 'shipping_charge', 'final_total',
            'return_reason', 'tracking_number', 'carrier',
            'refund_amount', 'refund_status',
            'items', 'created_at', 'updated_at',
        ]


class CheckoutSerializer(serializers.Serializer):
    """Input serializer for placing an order."""
    full_name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField()
    city = serializers.CharField(max_length=100)
    postal_code = serializers.CharField(max_length=20, required=False, default='')
    payment_method = serializers.ChoiceField(choices=['cod', 'card', 'mobile'], default='cod')
    address_id = serializers.IntegerField(required=False, help_text='Use a saved address by ID')


class ReturnRequestSerializer(serializers.Serializer):
    reason = serializers.CharField(min_length=10)
