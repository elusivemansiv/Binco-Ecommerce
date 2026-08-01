from django.urls import path
from . import views

urlpatterns = [
    path('config/general/', views.GeneralSettingsView.as_view(), name='api_general_settings'),
    path('config/payment-methods/', views.PaymentGatewaySettingsView.as_view(), name='api_payment_methods'),
    path('config/styles/', views.WebsiteStyleSettingsView.as_view(), name='api_style_settings'),
]
