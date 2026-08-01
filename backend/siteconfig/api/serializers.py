from rest_framework import serializers
from siteconfig.models import GeneralSettings, PaymentGatewaySettings, WebsiteStyleSettings


class GeneralSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralSettings
        fields = [
            'site_name', 'tagline', 'support_email', 'support_phone',
            'whatsapp_number', 'address', 'logo', 'favicon',
            'facebook_url', 'twitter_url', 'instagram_url', 'youtube_url',
            'footer_text',
        ]


class PaymentGatewaySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGatewaySettings
        fields = [
            'cod_enabled', 'sslcommerz_enabled', 'bkash_enabled', 'nagad_enabled',
            'stripe_enabled',
        ]


class WebsiteStyleSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteStyleSettings
        fields = [
            'header_style', 'hero_style', 'product_card_style',
            'footer_style', 'mobile_nav_style',
        ]

