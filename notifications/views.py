from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Notification


@login_required(login_url='login')
def notification_list(request):
    """User's notification center page."""
    notifications = Notification.objects.filter(user=request.user, channel='in_app')
    unread_count = notifications.filter(is_read=False).count()

    context = {
        'notifications': notifications[:50],
        'unread_count': unread_count,
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required(login_url='login')
def mark_notification_read(request, notification_id):
    """Mark a single notification as read (AJAX)."""
    notif = get_object_or_404(Notification, id=notification_id, user=request.user)
    notif.is_read = True
    notif.read_at = timezone.now()
    notif.save(update_fields=['is_read', 'read_at'])

    if notif.link:
        return JsonResponse({'status': 'success', 'redirect': notif.link})
    return JsonResponse({'status': 'success'})


@login_required(login_url='login')
def mark_all_read(request):
    """Mark all notifications as read (AJAX)."""
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True, read_at=timezone.now()
    )
    return JsonResponse({'status': 'success'})


@login_required(login_url='login')
def notification_count(request):
    """Return unread notification count (for navbar badge polling)."""
    count = Notification.objects.filter(
        user=request.user, channel='in_app', is_read=False
    ).count()
    return JsonResponse({'count': count})


@login_required(login_url='login')
def notification_dropdown(request):
    """Return latest notifications for the navbar dropdown (AJAX)."""
    notifs = Notification.objects.filter(
        user=request.user, channel='in_app'
    )[:7]

    data = []
    for n in notifs:
        data.append({
            'id': n.id,
            'title': n.title,
            'message': n.message[:100],
            'icon': n.icon,
            'link': n.link,
            'is_read': n.is_read,
            'time_ago': _time_ago(n.created_at),
        })

    unread = Notification.objects.filter(user=request.user, channel='in_app', is_read=False).count()
    return JsonResponse({'notifications': data, 'unread_count': unread})


def _time_ago(dt):
    """Human-friendly relative time."""
    diff = timezone.now() - dt
    seconds = diff.total_seconds()
    if seconds < 60:
        return 'Just now'
    elif seconds < 3600:
        mins = int(seconds // 60)
        return f'{mins}m ago'
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f'{hours}h ago'
    else:
        days = int(seconds // 86400)
        return f'{days}d ago'
