from rest_framework import generics, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from catalog.models import Product, Category
from .serializers import (
    ProductListSerializer, ProductDetailSerializer, CategorySerializer,
)


class CategoryListView(generics.ListAPIView):
    """List all categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # Categories are usually a small set


class ProductListView(generics.ListAPIView):
    """
    List active products with filtering, search, and ordering.

    Query params:
    - q: Search term (name, description)
    - category: Category slug
    - min_price / max_price: Price range
    - sort: newest, oldest, price_asc, price_desc
    - is_featured: true/false
    """
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'discount_price']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related('category', 'seller')
        # Custom filters
        category = self.request.query_params.get('category')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        is_featured = self.request.query_params.get('is_featured')
        q = self.request.query_params.get('q')

        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        if category:
            qs = qs.filter(category__slug=category)
        if min_price:
            try:
                qs = qs.filter(price__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                qs = qs.filter(price__lte=float(max_price))
            except ValueError:
                pass
        if is_featured and is_featured.lower() == 'true':
            qs = qs.filter(is_featured=True)

        # Sort
        sort = self.request.query_params.get('sort', 'newest')
        if sort == 'price_asc':
            qs = qs.order_by('price')
        elif sort == 'price_desc':
            qs = qs.order_by('-price')
        elif sort == 'oldest':
            qs = qs.order_by('created_at')
        else:
            qs = qs.order_by('-created_at')

        return qs


class ProductDetailView(generics.RetrieveAPIView):
    """Retrieve a single product by slug with full details."""
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related(
            'category', 'seller'
        ).prefetch_related(
            'colors', 'sizes', 'variations__color', 'variations__size',
            'extra_images__color', 'reviews',
        )


class ProductSearchSuggestionsView(generics.ListAPIView):
    """Return lightweight search suggestions (autocomplete)."""
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        q = self.request.query_params.get('q', '').strip()
        if len(q) < 2:
            return Product.objects.none()
        return Product.objects.filter(
            is_active=True, name__icontains=q
        ).only('id', 'name', 'slug', 'image', 'price', 'discount_price')[:8]


class FeaturedProductsView(generics.ListAPIView):
    """List featured products (for homepage)."""
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Product.objects.filter(is_active=True, is_featured=True)[:8]


class DealProductsView(generics.ListAPIView):
    """List products with discounts (for homepage deals section)."""
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Product.objects.filter(is_active=True, discount_price__isnull=False)[:8]
