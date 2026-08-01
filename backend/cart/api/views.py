from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from cart.models import Cart, CartItem, Coupon
from catalog.models import Product, ProductVariation
from store.models import ShippingConfig
from .serializers import CartSerializer, AddToCartSerializer, UpdateCartItemSerializer, ApplyCouponSerializer


class CartView(APIView):
    """Get the current user's cart with items, totals, and shipping info."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart, context={'request': request})

        # Calculate coupon discount
        coupon_code = request.session.get('coupon_code')
        discount_percent = 0
        discount_amount = 0
        if coupon_code:
            try:
                now = timezone.now()
                coupon = Coupon.objects.get(code=coupon_code, is_active=True,
                                           valid_from__lte=now, valid_to__gte=now)
                discount_percent = coupon.discount_percent
                discount_amount = float(cart.total) * discount_percent / 100
            except Coupon.DoesNotExist:
                coupon_code = None

        # Shipping
        shipping_conf = ShippingConfig.get_config()
        shipping_charge = float(shipping_conf.shipping_charge) if cart.total < shipping_conf.free_shipping_threshold else 0

        return Response({
            **serializer.data,
            'coupon_code': coupon_code,
            'discount_percent': discount_percent,
            'discount_amount': round(discount_amount, 2),
            'shipping_charge': shipping_charge,
            'free_shipping_threshold': float(shipping_conf.free_shipping_threshold),
            'final_total': round(float(cart.total) - discount_amount + shipping_charge, 2),
        })


class AddToCartView(APIView):
    """Add a product to the cart."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        product = get_object_or_404(Product, id=data['product_id'], is_active=True)
        cart, _ = Cart.objects.get_or_create(user=request.user)

        color_name = data.get('color', '')
        size_name = data.get('size', '')

        # Stock validation
        variation = ProductVariation.objects.filter(
            product=product,
            color__name=color_name if color_name else None,
            size__name=size_name if size_name else None
        ).first()

        if variation:
            if variation.stock < data['quantity']:
                return Response({'detail': f'Only {variation.stock} items available for this variant.'},
                                status=status.HTTP_400_BAD_REQUEST)
        elif product.variations.exists():
            return Response({'detail': 'Please select a valid color and size.'},
                            status=status.HTTP_400_BAD_REQUEST)
        elif product.stock < data['quantity']:
            return Response({'detail': f'Only {product.stock} items available.'},
                            status=status.HTTP_400_BAD_REQUEST)

        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, color=color_name, size=size_name
        )
        if not created:
            item.quantity += data['quantity']
            item.save()

        cart_serializer = CartSerializer(cart, context={'request': request})
        return Response({
            'detail': f'"{product.name}" added to cart.',
            'cart': cart_serializer.data,
        }, status=status.HTTP_201_CREATED)


class UpdateCartItemView(APIView):
    """Update a cart item's quantity or remove it (quantity=0)."""
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, item_id):
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qty = serializer.validated_data['quantity']

        if qty <= 0:
            item.delete()
            return Response({'detail': 'Item removed from cart.'})

        # Stock check
        variation = ProductVariation.objects.filter(
            product=item.product,
            color__name=item.color if item.color else None,
            size__name=item.size if item.size else None
        ).first()
        current_stock = variation.stock if variation else item.product.stock
        if qty > current_stock:
            return Response({'detail': f'Only {current_stock} items available.'},
                            status=status.HTTP_400_BAD_REQUEST)

        item.quantity = qty
        item.save()
        cart_serializer = CartSerializer(item.cart, context={'request': request})
        return Response(cart_serializer.data)

    def delete(self, request, item_id):
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        item.delete()
        return Response({'detail': 'Item removed from cart.'}, status=status.HTTP_204_NO_CONTENT)


class ApplyCouponView(APIView):
    """Apply or remove a coupon code."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ApplyCouponSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code'].strip().upper()
        try:
            now = timezone.now()
            coupon = Coupon.objects.get(code=code, is_active=True,
                                       valid_from__lte=now, valid_to__gte=now)
            request.session['coupon_code'] = code
            return Response({
                'detail': f'Coupon "{code}" applied! {coupon.discount_percent}% off.',
                'discount_percent': coupon.discount_percent,
            })
        except Coupon.DoesNotExist:
            return Response({'detail': 'Invalid or expired coupon code.'},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        request.session.pop('coupon_code', None)
        return Response({'detail': 'Coupon removed.'})
