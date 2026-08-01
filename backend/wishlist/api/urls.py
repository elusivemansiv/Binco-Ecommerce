from django.urls import path
from . import views

urlpatterns = [
    path('wishlist/', views.WishlistView.as_view(), name='api_wishlist'),
    path('wishlist/<int:product_id>/', views.WishlistToggleView.as_view(), name='api_wishlist_toggle'),
]
