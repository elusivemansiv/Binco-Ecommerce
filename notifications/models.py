from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    """System notification record — tracks every notification sent."""

    TYPE_CHOICES = [
        ('order_confirmation', 'Order Confirmation'),
        ('order_status', 'Order Status Update'),
        ('shipping_update', 'Shipping Update'),
        ('delivery_confirmation', 'Delivery Confirmation'),
        ('return_update', 'Return Update'),
        ('promotion', 'Promotion'),
        ('welcome', 'Welcome'),
        ('system', 'System Alert'),
    ]

    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('read', 'Read'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default='in_app')
    title = models.CharField(max_length=300)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, help_text='URL to redirect when notification is clicked')
    icon = models.CharField(max_length=50, blank=True, default='fa-bell', help_text='FontAwesome icon class')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_read = models.BooleanField(default=False)
    metadata = models.JSONField(blank=True, null=True, help_text='Extra data (order_id, tracking_number, etc.)')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'[{self.get_channel_display()}] {self.title}'


class NotificationTemplate(models.Model):
    """Reusable notification templates for each event type."""

    EVENT_CHOICES = [
        ('order_placed', 'Order Placed'),
        ('order_processing', 'Order Processing'),
        ('order_shipped', 'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('order_cancelled', 'Order Cancelled'),
        ('return_requested', 'Return Requested'),
        ('return_approved', 'Return Approved'),
        ('welcome_user', 'New User Welcome'),
        ('promotion_blast', 'Promotional Blast'),
    ]

    event = models.CharField(max_length=30, choices=EVENT_CHOICES, unique=True)
    email_subject = models.CharField(max_length=300, blank=True)
    email_body = models.TextField(blank=True, help_text='HTML email body. Use {{order_id}}, {{customer_name}}, {{total}}, {{status}} as placeholders.')
    sms_body = models.CharField(max_length=500, blank=True, help_text='SMS text. Use {{order_id}}, {{customer_name}} as placeholders.')
    push_title = models.CharField(max_length=200, blank=True)
    push_body = models.CharField(max_length=500, blank=True)
    in_app_title = models.CharField(max_length=200, blank=True)
    in_app_message = models.TextField(blank=True)
    in_app_icon = models.CharField(max_length=50, blank=True, default='fa-bell')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
        ordering = ['event']

    def __str__(self):
        return self.get_event_display()


class PushSubscription(models.Model):
    """Store browser push notification subscriptions."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_subscriptions')
    endpoint = models.URLField(max_length=500)
    p256dh_key = models.CharField(max_length=200)
    auth_key = models.CharField(max_length=200)
    browser = models.CharField(max_length=50, blank=True)
    device = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Push Subscription'
        verbose_name_plural = 'Push Subscriptions'

    def __str__(self):
        return f'{self.user.username} – {self.browser or "Unknown"}'
