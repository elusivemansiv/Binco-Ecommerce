from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='api_cart'),
    path('cart/items/', views.AddToCartView.as_view(), name='api_add_to_cart'),
    path('cart/items/<int:item_id>/', views.UpdateCartItemView.as_view(), name='api_update_cart_item'),
    path('cart/coupon/', views.ApplyCouponView.as_view(), name='api_coupon'),
]
