from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from orders.models import Order, OrderItem
from cart.models import Cart, Coupon
from catalog.models import ProductVariation
from store.models import ShippingConfig
from accounts.models import UserAddress
from .serializers import (
    OrderListSerializer, OrderDetailSerializer,
    CheckoutSerializer, ReturnRequestSerializer,
)


class OrderListView(generics.ListAPIView):
    """List the current user's orders."""
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Order.objects.filter(user=self.request.user).order_by('-created_at')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class OrderDetailView(generics.RetrieveAPIView):
    """Retrieve a single order with full details."""
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')


class CheckoutView(APIView):
    """Place an order from the user's cart."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.select_related('product').all()

        if not items.exists():
            return Response({'detail': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        # If address_id is provided, load from address book
        if data.get('address_id'):
            try:
                addr = UserAddress.objects.get(id=data['address_id'], user=request.user)
                data['full_name'] = addr.full_name
                data['phone'] = addr.phone
                data['address'] = addr.address
                data['city'] = addr.city
                data['postal_code'] = addr.postal_code
            except UserAddress.DoesNotExist:
                return Response({'detail': 'Address not found.'}, status=status.HTTP_400_BAD_REQUEST)

        # Stock validation
        for item in items:
            variation = ProductVariation.objects.filter(
                product=item.product,
                color__name=item.color if item.color else None,
                size__name=item.size if item.size else None
            ).first()
            stock_available = variation.stock if variation else item.product.stock
            if stock_available < item.quantity:
                return Response({
                    'detail': f'"{item.product.name}" only has {stock_available} left in stock.'
                }, status=status.HTTP_400_BAD_REQUEST)

        # Coupon handling
        coupon_code = request.session.get('coupon_code')
        discount_amount = 0
        coupon_obj = None
        if coupon_code:
            try:
                now = timezone.now()
                coupon_obj = Coupon.objects.get(code=coupon_code, is_active=True,
                                               valid_from__lte=now, valid_to__gte=now)
                discount_amount = float(cart.total) * coupon_obj.discount_percent / 100
            except Coupon.DoesNotExist:
                pass

        # Shipping
        shipping_conf = ShippingConfig.get_config()
        shipping_charge = float(shipping_conf.shipping_charge) if cart.total < shipping_conf.free_shipping_threshold else 0

        # Create order
        order = Order.objects.create(
            user=request.user,
            coupon=coupon_obj,
            full_name=data['full_name'],
            email=data['email'],
            phone=data['phone'],
            address=data['address'],
            city=data['city'],
            postal_code=data.get('postal_code', ''),
            total_price=cart.total,
            discount_amount=discount_amount,
            shipping_charge=shipping_charge,
            payment_method=data['payment_method'],
        )

        # Create order items & deduct stock
        for item in items:
            variation = ProductVariation.objects.filter(
                product=item.product,
                color__name=item.color if item.color else None,
                size__name=item.size if item.size else None
            ).first()
            if variation:
                variation.stock -= item.quantity
                variation.save(update_fields=['stock'])
            else:
                item.product.stock -= item.quantity
                item.product.save(update_fields=['stock'])

            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                price=item.product.effective_price,
                quantity=item.quantity,
                color=item.color,
                size=item.size,
            )

        # Finalize
        if coupon_obj:
            coupon_obj.used_count += 1
            coupon_obj.save()
        items.delete()
        request.session.pop('coupon_code', None)

        # Notifications
        try:
            from notifications.services import NotificationService
            NotificationService.notify_order_placed(order)
            NotificationService.notify_seller_new_order(order)
        except Exception:
            pass

        return Response(
            OrderDetailSerializer(order, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class ReturnRequestView(APIView):
    """Request a return for a delivered/shipped order."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)
        if order.status not in ['shipped', 'delivered']:
            return Response({'detail': 'Only shipped or delivered orders can be returned.'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = ReturnRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order.status = 'return_requested'
        order.return_reason = serializer.validated_data['reason']
        order.save()

        return Response({'detail': 'Return request submitted successfully.'})


class OrderTrackingView(APIView):
    """Get tracking information for an order."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)
        return Response({
            'order_id': order.id,
            'status': order.status,
            'status_display': order.get_status_display(),
            'tracking_number': order.tracking_number,
            'carrier': order.carrier,
            'created_at': order.created_at,
            'updated_at': order.updated_at,
        })
