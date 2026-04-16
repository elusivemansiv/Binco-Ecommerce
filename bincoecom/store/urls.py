from django.urls import path
from . import views
from accounts import views as accounts_views

urlpatterns = [
    # Home & Products
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/review/', views.submit_review, name='submit_review'),

    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/coupon/', views.apply_coupon, name='apply_coupon'),
    path('cart/coupon/remove/', views.remove_coupon, name='remove_coupon'),

    # Checkout & Orders
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('order/history/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/invoice/', views.generate_invoice, name='generate_invoice'),
    path('become-seller/', accounts_views.become_seller, name='become_seller'),
    path('orders/<int:order_id>/request-return/', views.request_return, name='request_return'),

    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),

    # Seller
    path('seller/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/orders/', views.seller_orders, name='seller_orders'),
    path('seller/products/', views.seller_products, name='seller_products'),
    path('seller/product/add/', views.add_product, name='add_product'),
    path('seller/product/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('seller/product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('seller/add-color/', views.ajax_add_color, name='ajax_add_color'),
    path('seller/add-size/', views.ajax_add_size, name='ajax_add_size'),
    path('seller/order/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
]