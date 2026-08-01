from django.urls import path
from . import views

urlpatterns = [
    path('catalog/categories/', views.CategoryListView.as_view(), name='api_category_list'),
    path('catalog/products/', views.ProductListView.as_view(), name='api_product_list'),
    path('catalog/products/featured/', views.FeaturedProductsView.as_view(), name='api_featured_products'),
    path('catalog/products/deals/', views.DealProductsView.as_view(), name='api_deal_products'),
    path('catalog/products/search-suggestions/', views.ProductSearchSuggestionsView.as_view(), name='api_search_suggestions'),
    path('catalog/products/<slug:slug>/', views.ProductDetailView.as_view(), name='api_product_detail'),
]
