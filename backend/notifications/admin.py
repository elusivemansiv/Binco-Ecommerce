from django.contrib import admin
from .models import Notification, NotificationTemplate, PushSubscription


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'channel', 'status', 'is_read', 'created_at')
    list_filter = ('notification_type', 'channel', 'status', 'is_read')
    search_fields = ('title', 'message', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'sent_at', 'read_at')
    list_per_page = 30
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('user', 'notification_type', 'channel', 'title', 'message'),
        }),
        ('Status', {
            'fields': ('status', 'is_read', 'link', 'icon'),
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'sent_at', 'read_at'),
        }),
    )

    actions = ['mark_as_read', 'mark_as_sent', 'resend_notifications']

    @admin.action(description='Mark selected as read')
    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_read=True, read_at=timezone.now())

    @admin.action(description='Mark selected as sent')
    def mark_as_sent(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='sent', sent_at=timezone.now())

    @admin.action(description='Resend failed notifications')
    def resend_notifications(self, request, queryset):
        failed = queryset.filter(status='failed')
        count = failed.count()
        # Reset to pending for retry
        failed.update(status='pending')
        self.message_user(request, f'{count} notification(s) queued for retry.')


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('event', 'email_subject', 'is_active')
    list_filter = ('is_active',)
    list_editable = ('is_active',)
    search_fields = ('event', 'email_subject')

    fieldsets = (
        ('Event', {
            'fields': ('event', 'is_active'),
        }),
        ('Email Template', {
            'fields': ('email_subject', 'email_body'),
            'description': 'Available placeholders: {{order_id}}, {{customer_name}}, {{total}}, {{status}}, {{payment_method}}',
        }),
        ('SMS Template', {
            'fields': ('sms_body',),
        }),
        ('Push Notification', {
            'fields': ('push_title', 'push_body'),
            'classes': ('collapse',),
        }),
        ('In-App Notification', {
            'fields': ('in_app_title', 'in_app_message', 'in_app_icon'),
        }),
    )


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'browser', 'device', 'is_active', 'created_at')
    list_filter = ('is_active', 'browser')
    search_fields = ('user__username',)
