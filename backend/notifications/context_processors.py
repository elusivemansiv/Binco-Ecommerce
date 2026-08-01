from .models import Notification


def notification_context(request):
    """Inject unread notification count into every template."""
    if request.user.is_authenticated:
        unread = Notification.objects.filter(
            user=request.user, channel='in_app', is_read=False
        ).count()
        return {'unread_notification_count': unread}
    return {'unread_notification_count': 0}
