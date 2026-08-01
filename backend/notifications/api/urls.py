from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.NotificationListView.as_view(), name='api_notification_list'),
    path('notifications/count/', views.NotificationCountView.as_view(), name='api_notification_count'),
    path('notifications/<int:pk>/read/', views.MarkNotificationReadView.as_view(), name='api_mark_read'),
    path('notifications/read-all/', views.MarkAllReadView.as_view(), name='api_mark_all_read'),
    path('notifications/push/subscribe/', views.PushSubscribeView.as_view(), name='api_push_subscribe'),
]
