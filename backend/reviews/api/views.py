from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from catalog.models import Product
from reviews.models import ProductReview
from .serializers import ProductReviewSerializer, CreateReviewSerializer


class ProductReviewListView(generics.ListAPIView):
    """List reviews for a specific product."""
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return ProductReview.objects.filter(product_id=product_id).order_by('-created_at')


class ProductReviewCreateView(generics.CreateAPIView):
    """Submit or update a review for a product."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        serializer = CreateReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review, created = ProductReview.objects.update_or_create(
            product=product, user=request.user,
            defaults={
                'rating': serializer.validated_data['rating'],
                'comment': serializer.validated_data['comment'],
            }
        )
        return Response(
            ProductReviewSerializer(review).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
