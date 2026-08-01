from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from wishlist.models import Wishlist
from catalog.models import Product
from catalog.api.serializers import ProductListSerializer


class WishlistView(APIView):
    """Get the current user's wishlist."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        products = wishlist.products.filter(is_active=True)
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response({
            'count': products.count(),
            'products': serializer.data,
        })


class WishlistToggleView(APIView):
    """Add or remove a product from the wishlist (toggle)."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, is_active=True)
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

        if product in wishlist.products.all():
            wishlist.products.remove(product)
            return Response({
                'detail': f'"{product.name}" removed from wishlist.',
                'in_wishlist': False,
                'wishlist_count': wishlist.products.count(),
            })
        else:
            wishlist.products.add(product)
            return Response({
                'detail': f'"{product.name}" added to wishlist!',
                'in_wishlist': True,
                'wishlist_count': wishlist.products.count(),
            }, status=status.HTTP_201_CREATED)

    def delete(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        wishlist.products.remove(product)
        return Response({
            'detail': f'"{product.name}" removed from wishlist.',
            'wishlist_count': wishlist.products.count(),
        })
