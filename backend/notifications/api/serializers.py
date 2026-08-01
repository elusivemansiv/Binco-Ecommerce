from rest_framework import serializers
from notifications.models import Notification, PushSubscription


class NotificationSerializer(serializers.ModelSerializer):
    time_ago = serializers.SerializerMethodField()
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'type_display', 'title', 'message',
                  'link', 'icon', 'is_read', 'created_at', 'time_ago']

    def get_time_ago(self, obj):
        from django.utils import timezone
        diff = timezone.now() - obj.created_at
        seconds = diff.total_seconds()
        if seconds < 60:
            return 'Just now'
        elif seconds < 3600:
            return f'{int(seconds // 60)}m ago'
        elif seconds < 86400:
            return f'{int(seconds // 3600)}h ago'
        else:
            return f'{int(seconds // 86400)}d ago'


class PushSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushSubscription
        fields = ['id', 'endpoint', 'p256dh_key', 'auth_key', 'browser', 'device']
