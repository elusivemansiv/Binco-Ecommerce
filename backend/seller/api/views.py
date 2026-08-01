from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Sum, F
from django.utils import timezone
from catalog.models import Product, ProductVariation, ProductImage
from orders.models import Order, OrderItem
from .serializers import (
    SellerProductSerializer, SellerProductCreateSerializer,
    SellerVariationSerializer, SellerProductImageSerializer,
    SellerOrderSerializer, UpdateOrderStatusSerializer,
)


class IsSeller(permissions.BasePermission):
    """Allows access only to authenticated sellers."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.profile.is_seller)


class DashboardStatsView(APIView):
    """Get high-level stats for the seller dashboard."""
    permission_classes = [IsSeller]

    def get(self, request):
        user = request.user
        delivered_items = OrderItem.objects.filter(
            product__seller=user, order__status='delivered'
        )
        total_earnings = delivered_items.aggregate(
            total=Sum(F('price') * F('quantity'))
        )['total'] or 0

        active_orders = Order.objects.filter(
            items__product__seller=user,
            status__in=['pending', 'processing', 'shipped']
        ).distinct().count()

        product_count = Product.objects.filter(seller=user).count()

        recent_orders = Order.objects.filter(
            items__product__seller=user
        ).distinct().order_by('-created_at')[:5]

        # Serialize recent orders minimally
        recent_data = []
        for order in recent_orders:
            recent_data.append({
                'id': order.id,
                'customer': order.full_name,
                'status_display': order.get_status_display(),
                'date': order.created_at,
            })

        return Response({
            'total_earnings': total_earnings,
            'active_orders': active_orders,
            'total_products': product_count,
            'recent_orders': recent_data,
        })


class SellerProductListView(generics.ListCreateAPIView):
    """List seller's products or create a new one."""
    permission_classes = [IsSeller]

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user).order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SellerProductCreateSerializer
        return SellerProductSerializer

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class SellerProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a seller's product."""
    permission_classes = [IsSeller]

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SellerProductCreateSerializer
        return SellerProductSerializer


class SellerVariationListView(generics.ListCreateAPIView):
    """Manage variations for a specific product."""
    serializer_class = SellerVariationSerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        return ProductVariation.objects.filter(
            product_id=self.kwargs['product_id'],
            product__seller=self.request.user
        )

    def perform_create(self, serializer):
        product = get_object_or_404(Product, id=self.kwargs['product_id'], seller=self.request.user)
        serializer.save(product=product)


class SellerVariationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Update or delete a specific variation."""
    serializer_class = SellerVariationSerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        return ProductVariation.objects.filter(product__seller=self.request.user)


class SellerOrderListView(APIView):
    """List orders containing the seller's products."""
    permission_classes = [IsSeller]

    def get(self, request):
        status_filter = request.query_params.get('status')
        orders_qs = Order.objects.filter(items__product__seller=request.user).distinct().order_by('-created_at')
        
        if status_filter:
            orders_qs = orders_qs.filter(status=status_filter)

        # Pagination could be added here manually or by switching to generics.ListAPIView
        
        results = []
        for order in orders_qs[:50]:  # Cap at 50 for now
            seller_items = order.items.filter(product__seller=request.user)
            seller_total = sum([item.price * item.quantity for item in seller_items])
            
            results.append({
                'order_id': order.id,
                'customer_name': order.full_name,
                'status': order.status,
                'status_display': order.get_status_display(),
                'payment_method': order.get_payment_method_display(),
                'created_at': order.created_at,
                'seller_total': seller_total,
                'items': [
                    {
                        'id': item.id,
                        'product_name': item.product_name,
                        'price': item.price,
                        'quantity': item.quantity,
                        'color': item.color,
                        'size': item.size,
                        'subtotal': item.price * item.quantity,
                    } for item in seller_items
                ]
            })

        return Response(results)


class SellerOrderStatusUpdateView(APIView):
    """Seller updates order status (only certain transitions allowed)."""
    permission_classes = [IsSeller]

    def put(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, items__product__seller=request.user)
        serializer = UpdateOrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['status']

        if order.status in ['pending', 'processing']:
            if new_status not in ['pending', 'processing', 'cancelled']:
                return Response({'detail': 'Invalid status transition.'}, status=status.HTTP_400_BAD_REQUEST)
        elif order.status == 'return_requested':
            if new_status not in ['return_requested', 'return_approved']:
                return Response({'detail': 'Sellers can only approve returns.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Cannot change status of this order.'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()
        
        try:
            from notifications.services import NotificationService
            NotificationService.notify_order_status_change(order)
        except Exception:
            pass

        return Response({'detail': 'Order status updated.', 'new_status': order.get_status_display()})

