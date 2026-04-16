from django.db import models
from django.core.cache import cache


class SingletonModel(models.Model):
    """Base class for singleton models — only one row should ever exist."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Force the PK to 1 so we always update the same row
        self.pk = 1
        super().save(*args, **kwargs)
        # Bust cache on save
        cache.delete(self._cache_key())

    def delete(self, *args, **kwargs):
        pass  # Prevent deletion

    @classmethod
    def _cache_key(cls):
        return f'siteconfig_{cls.__name__}'

    @classmethod
    def get(cls):
        """Retrieve the singleton. Uses cache for performance."""
        key = cls._cache_key()
        obj = cache.get(key)
        if obj is None:
            obj, _ = cls.objects.get_or_create(pk=1)
            cache.set(key, obj, timeout=3600)
        return obj


# ────────────────────── GENERAL SETTINGS ──────────────────────
class GeneralSettings(SingletonModel):
    site_name = models.CharField(max_length=200, default='Binco Ecommerce')
    tagline = models.CharField(max_length=300, blank=True, default='Bangladesh\'s Trusted Marketplace')
    logo = models.ImageField(upload_to='config/logos/', blank=True, null=True)
    favicon = models.ImageField(upload_to='config/favicons/', blank=True, null=True)
    support_email = models.EmailField(default='support@binco.com')
    support_phone = models.CharField(max_length=30, default='+880 1700-000000')
    address = models.TextField(blank=True, default='Dhaka, Bangladesh')
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    footer_text = models.CharField(max_length=500, blank=True, default='© 2025 Binco Ecommerce. All rights reserved.')
    maintenance_mode = models.BooleanField(default=False, help_text='Enable to show a maintenance page to visitors.')
    meta_description = models.CharField(max_length=300, blank=True, default='Binco is Bangladesh\'s leading marketplace to buy and sell new and used items.')
    google_analytics_id = models.CharField(max_length=50, blank=True, help_text='e.g. G-XXXXXXXXXX')

    class Meta:
        verbose_name = 'General Settings'
        verbose_name_plural = 'General Settings'

    def __str__(self):
        return self.site_name


# ────────────────────── CURRENCY & TAX ────────────────────────
class CurrencyTaxSettings(SingletonModel):
    CURRENCY_CHOICES = [
        ('BDT', '৳ BDT – Bangladeshi Taka'),
        ('USD', '$ USD – US Dollar'),
        ('EUR', '€ EUR – Euro'),
        ('GBP', '£ GBP – British Pound'),
        ('INR', '₹ INR – Indian Rupee'),
    ]
    currency_code = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default='BDT')
    currency_symbol = models.CharField(max_length=5, default='৳')
    currency_position = models.CharField(
        max_length=10,
        choices=[('before', 'Before price (৳100)'), ('after', 'After price (100৳)')],
        default='before',
    )
    tax_enabled = models.BooleanField(default=False)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text='Tax percentage (e.g. 15.00 for 15%)')
    tax_label = models.CharField(max_length=50, default='VAT', help_text='Label shown on invoices/cart (e.g. VAT, GST, Tax)')
    tax_included_in_price = models.BooleanField(default=True, help_text='If True, prices already include tax.')

    class Meta:
        verbose_name = 'Currency & Tax Settings'
        verbose_name_plural = 'Currency & Tax Settings'

    def __str__(self):
        return f'{self.currency_symbol} {self.currency_code} | Tax: {self.tax_rate}%'


# ────────────────────── PAYMENT GATEWAYS ──────────────────────
class PaymentGatewaySettings(SingletonModel):
    # Cash on Delivery
    cod_enabled = models.BooleanField(default=True, verbose_name='Cash on Delivery Enabled')
    cod_label = models.CharField(max_length=100, default='Cash on Delivery')
    cod_instructions = models.TextField(blank=True, default='Pay with cash when your order is delivered.')

    # bKash
    bkash_enabled = models.BooleanField(default=False, verbose_name='bKash Enabled')
    bkash_merchant_number = models.CharField(max_length=20, blank=True)
    bkash_api_key = models.CharField(max_length=200, blank=True)
    bkash_api_secret = models.CharField(max_length=200, blank=True)
    bkash_sandbox = models.BooleanField(default=True, help_text='Use sandbox/test mode')

    # Nagad
    nagad_enabled = models.BooleanField(default=False, verbose_name='Nagad Enabled')
    nagad_merchant_number = models.CharField(max_length=20, blank=True)
    nagad_api_key = models.CharField(max_length=200, blank=True)

    # Stripe / Card
    stripe_enabled = models.BooleanField(default=False, verbose_name='Stripe (Card) Enabled')
    stripe_publishable_key = models.CharField(max_length=200, blank=True)
    stripe_secret_key = models.CharField(max_length=200, blank=True)
    stripe_webhook_secret = models.CharField(max_length=200, blank=True)
    stripe_sandbox = models.BooleanField(default=True, help_text='Use test mode keys')

    # SSLCommerz
    sslcommerz_enabled = models.BooleanField(default=False, verbose_name='SSLCommerz Enabled')
    sslcommerz_store_id = models.CharField(max_length=200, blank=True)
    sslcommerz_store_passwd = models.CharField(max_length=200, blank=True)
    sslcommerz_sandbox = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Payment Gateway Settings'
        verbose_name_plural = 'Payment Gateway Settings'

    def __str__(self):
        enabled = []
        if self.cod_enabled:
            enabled.append('COD')
        if self.bkash_enabled:
            enabled.append('bKash')
        if self.nagad_enabled:
            enabled.append('Nagad')
        if self.stripe_enabled:
            enabled.append('Stripe')
        if self.sslcommerz_enabled:
            enabled.append('SSLCommerz')
        return f'Active: {", ".join(enabled) or "None"}'


# ────────────────────── EMAIL CONFIGURATION ───────────────────
class EmailSettings(SingletonModel):
    EMAIL_BACKEND_CHOICES = [
        ('console', 'Console (Development)'),
        ('smtp', 'SMTP Server'),
        ('sendgrid', 'SendGrid API'),
        ('ses', 'Amazon SES'),
    ]
    backend = models.CharField(max_length=20, choices=EMAIL_BACKEND_CHOICES, default='console')
    from_email = models.EmailField(default='noreply@binco.com')
    from_name = models.CharField(max_length=100, default='Binco Ecommerce')

    # SMTP
    smtp_host = models.CharField(max_length=200, blank=True, default='smtp.gmail.com')
    smtp_port = models.PositiveIntegerField(default=587)
    smtp_username = models.CharField(max_length=200, blank=True)
    smtp_password = models.CharField(max_length=200, blank=True)
    smtp_use_tls = models.BooleanField(default=True)

    # SendGrid
    sendgrid_api_key = models.CharField(max_length=200, blank=True)

    # Toggle email types
    send_order_confirmation = models.BooleanField(default=True)
    send_shipping_update = models.BooleanField(default=True)
    send_welcome_email = models.BooleanField(default=True)
    send_promotional_emails = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Email Configuration'
        verbose_name_plural = 'Email Configuration'

    def __str__(self):
        return f'Email: {self.backend} ({self.from_email})'


# ────────────────────── SMS CONFIGURATION ─────────────────────
class SMSSettings(SingletonModel):
    SMS_PROVIDER_CHOICES = [
        ('disabled', 'Disabled'),
        ('twilio', 'Twilio'),
        ('bulksmsbd', 'BulkSMS BD'),
        ('sslwireless', 'SSL Wireless'),
    ]
    provider = models.CharField(max_length=20, choices=SMS_PROVIDER_CHOICES, default='disabled')

    # Twilio
    twilio_account_sid = models.CharField(max_length=200, blank=True)
    twilio_auth_token = models.CharField(max_length=200, blank=True)
    twilio_from_number = models.CharField(max_length=20, blank=True)

    # BulkSMS BD
    bulksms_api_key = models.CharField(max_length=200, blank=True)
    bulksms_sender_id = models.CharField(max_length=50, blank=True)

    # Toggle SMS types
    send_order_sms = models.BooleanField(default=True)
    send_shipping_sms = models.BooleanField(default=True)
    send_otp_sms = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'SMS Configuration'
        verbose_name_plural = 'SMS Configuration'

    def __str__(self):
        return f'SMS: {self.get_provider_display()}'
