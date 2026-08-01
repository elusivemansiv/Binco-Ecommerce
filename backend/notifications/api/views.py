from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from notifications.models import Notification, PushSubscription
from .serializers import NotificationSerializer, PushSubscriptionSerializer


class NotificationListView(generics.ListAPIView):
    """List the current user's in-app notifications."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user, channel='in_app'
        ).order_by('-created_at')


class NotificationCountView(APIView):
    """Get unread notification count."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            user=request.user, channel='in_app', is_read=False
        ).count()
        return Response({'count': count})


class MarkNotificationReadView(APIView):
    """Mark a single notification as read."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        notif = get_object_or_404(Notification, id=pk, user=request.user)
        notif.is_read = True
        notif.read_at = timezone.now()
        notif.save(update_fields=['is_read', 'read_at'])
        return Response({'detail': 'Notification marked as read.', 'link': notif.link})


class MarkAllReadView(APIView):
    """Mark all notifications as read."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        updated = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return Response({'detail': f'{updated} notifications marked as read.'})


class PushSubscribeView(generics.CreateAPIView):
    """Register a push notification subscription."""
    serializer_class = PushSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
