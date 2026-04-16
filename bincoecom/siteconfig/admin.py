from django.contrib import admin
from .models import (
    GeneralSettings, CurrencyTaxSettings,
    PaymentGatewaySettings, EmailSettings, SMSSettings
)


class SingletonAdmin(admin.ModelAdmin):
    """Base admin for singleton models — no add/delete, always redirect to change form."""

    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """Auto-redirect to the single object's change page."""
        obj = self.model.get()
        from django.shortcuts import redirect
        from django.urls import reverse
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        return redirect(reverse(f'admin:{app_label}_{model_name}_change', args=[obj.pk]))


@admin.register(GeneralSettings)
class GeneralSettingsAdmin(SingletonAdmin):
    fieldsets = (
        ('Site Identity', {
            'fields': ('site_name', 'tagline', 'logo', 'favicon'),
        }),
        ('Contact Info', {
            'fields': ('support_email', 'support_phone', 'address'),
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url', 'youtube_url'),
            'classes': ('collapse',),
        }),
        ('SEO & Analytics', {
            'fields': ('meta_description', 'google_analytics_id'),
            'classes': ('collapse',),
        }),
        ('Display', {
            'fields': ('footer_text', 'maintenance_mode'),
        }),
    )


@admin.register(CurrencyTaxSettings)
class CurrencyTaxSettingsAdmin(SingletonAdmin):
    fieldsets = (
        ('Currency', {
            'fields': ('currency_code', 'currency_symbol', 'currency_position'),
        }),
        ('Tax', {
            'fields': ('tax_enabled', 'tax_rate', 'tax_label', 'tax_included_in_price'),
        }),
    )


@admin.register(PaymentGatewaySettings)
class PaymentGatewaySettingsAdmin(SingletonAdmin):
    fieldsets = (
        ('Cash on Delivery', {
            'fields': ('cod_enabled', 'cod_label', 'cod_instructions'),
        }),
        ('bKash', {
            'fields': ('bkash_enabled', 'bkash_merchant_number', 'bkash_api_key', 'bkash_api_secret', 'bkash_sandbox'),
            'classes': ('collapse',),
        }),
        ('Nagad', {
            'fields': ('nagad_enabled', 'nagad_merchant_number', 'nagad_api_key'),
            'classes': ('collapse',),
        }),
        ('Stripe (International Cards)', {
            'fields': ('stripe_enabled', 'stripe_publishable_key', 'stripe_secret_key', 'stripe_webhook_secret', 'stripe_sandbox'),
            'classes': ('collapse',),
        }),
        ('SSLCommerz', {
            'fields': ('sslcommerz_enabled', 'sslcommerz_store_id', 'sslcommerz_store_passwd', 'sslcommerz_sandbox'),
            'classes': ('collapse',),
        }),
    )


@admin.register(EmailSettings)
class EmailSettingsAdmin(SingletonAdmin):
    fieldsets = (
        ('Provider', {
            'fields': ('backend', 'from_email', 'from_name'),
        }),
        ('SMTP Settings', {
            'fields': ('smtp_host', 'smtp_port', 'smtp_username', 'smtp_password', 'smtp_use_tls'),
            'classes': ('collapse',),
        }),
        ('SendGrid', {
            'fields': ('sendgrid_api_key',),
            'classes': ('collapse',),
        }),
        ('Email Toggles', {
            'fields': ('send_order_confirmation', 'send_shipping_update', 'send_welcome_email', 'send_promotional_emails'),
        }),
    )


@admin.register(SMSSettings)
class SMSSettingsAdmin(SingletonAdmin):
    fieldsets = (
        ('Provider', {
            'fields': ('provider',),
        }),
        ('Twilio', {
            'fields': ('twilio_account_sid', 'twilio_auth_token', 'twilio_from_number'),
            'classes': ('collapse',),
        }),
        ('BulkSMS BD', {
            'fields': ('bulksms_api_key', 'bulksms_sender_id'),
            'classes': ('collapse',),
        }),
        ('SMS Toggles', {
            'fields': ('send_order_sms', 'send_shipping_sms', 'send_otp_sms'),
        }),
    )
