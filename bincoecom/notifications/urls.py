from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('notifications/count/', views.notification_count, name='notification_count'),
    path('notifications/dropdown/', views.notification_dropdown, name='notification_dropdown'),
]
