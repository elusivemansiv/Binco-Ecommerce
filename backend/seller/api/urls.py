from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.DashboardStatsView.as_view(), name='api_seller_dashboard'),
    
    path('products/', views.SellerProductListView.as_view(), name='api_seller_products'),
    path('products/<int:pk>/', views.SellerProductDetailView.as_view(), name='api_seller_product_detail'),
    path('products/<int:product_id>/variations/', views.SellerVariationListView.as_view(), name='api_seller_variations'),
    path('variations/<int:pk>/', views.SellerVariationDetailView.as_view(), name='api_seller_variation_detail'),
    
    path('orders/', views.SellerOrderListView.as_view(), name='api_seller_orders'),
    path('orders/<int:order_id>/status/', views.SellerOrderStatusUpdateView.as_view(), name='api_seller_order_status'),
]
