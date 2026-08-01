from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.OrderListView.as_view(), name='api_order_list'),
    path('orders/checkout/', views.CheckoutView.as_view(), name='api_checkout'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='api_order_detail'),
    path('orders/<int:pk>/return/', views.ReturnRequestView.as_view(), name='api_return_request'),
    path('orders/<int:pk>/track/', views.OrderTrackingView.as_view(), name='api_order_tracking'),
]
