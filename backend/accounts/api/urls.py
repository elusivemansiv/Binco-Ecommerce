from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    path('auth/register/', views.RegisterView.as_view(), name='api_register'),
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='api_token_obtain'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    path('auth/logout/', views.LogoutView.as_view(), name='api_logout'),
    path('auth/password-change/', views.PasswordChangeView.as_view(), name='api_password_change'),

    # User Profile
    path('users/me/', views.UserMeView.as_view(), name='api_user_me'),
    path('users/me/become-seller/', views.BecomeSellerView.as_view(), name='api_become_seller'),
    path('users/me/verification/', views.SellerVerificationView.as_view(), name='api_seller_verification'),

    # Address Book
    path('users/me/addresses/', views.UserAddressListCreateView.as_view(), name='api_address_list'),
    path('users/me/addresses/<int:pk>/', views.UserAddressDetailView.as_view(), name='api_address_detail'),
]
