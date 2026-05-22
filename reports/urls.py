from django.urls import path
from . import views

urlpatterns = [
    path('admin/reports/', views.reports_dashboard, name='reports_dashboard'),
    path('admin/reports/export/csv/', views.export_sales_csv, name='export_sales_csv'),
    path('admin/reports/export/excel/', views.export_sales_excel, name='export_sales_excel'),
]
