from rest_framework import generics, permissions
from siteconfig.models import GeneralSettings, PaymentGatewaySettings, WebsiteStyleSettings
from .serializers import (
    GeneralSettingsSerializer, PaymentGatewaySettingsSerializer, WebsiteStyleSettingsSerializer
)


class GeneralSettingsView(generics.RetrieveAPIView):
    """Get general site configuration."""
    serializer_class = GeneralSettingsSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return GeneralSettings.get()


class PaymentGatewaySettingsView(generics.RetrieveAPIView):
    """Get available payment methods."""
    serializer_class = PaymentGatewaySettingsSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return PaymentGatewaySettings.get()


class WebsiteStyleSettingsView(generics.RetrieveAPIView):
    """Get dynamic styling options."""
    serializer_class = WebsiteStyleSettingsSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return WebsiteStyleSettings.get()

