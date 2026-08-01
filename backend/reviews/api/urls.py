from django.urls import path
from . import views

urlpatterns = [
    path('products/<int:product_id>/reviews/', views.ProductReviewListView.as_view(), name='api_product_reviews'),
    path('products/<int:product_id>/reviews/submit/', views.ProductReviewCreateView.as_view(), name='api_submit_review'),
]
