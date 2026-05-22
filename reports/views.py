import csv
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Avg, F
from django.utils import timezone
from datetime import timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side

from store.models import Order, OrderItem, Product
from django.contrib.auth.models import User
from .models import Expense

@staff_member_required
def reports_dashboard(request):
    # Date Range Handling
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # --- KPI Data ---
    delivered_orders = Order.objects.filter(status='delivered', created_at__gte=start_date)
    total_revenue = delivered_orders.aggregate(total=Sum('total_price'))['total'] or 0
    total_orders_count = delivered_orders.count()
    avg_order_value = total_revenue / total_orders_count if total_orders_count > 0 else 0
    
    total_expenses = Expense.objects.filter(date__gte=start_date).aggregate(total=Sum('amount'))['total'] or 0
    net_profit = float(total_revenue) - float(total_expenses)
    
    # --- Sales Distribution (Chart Data) ---
    sales_by_status = Order.objects.filter(created_at__gte=start_date).values('status').annotate(count=Count('id'))
    
    # --- Top Products ---
    top_products = OrderItem.objects.filter(order__status='delivered', order__created_at__gte=start_date) \
        .values('product__name') \
        .annotate(total_qty=Sum('quantity'), total_rev=Sum(F('price') * F('quantity'))) \
        .order_by('-total_rev')[:5]
        
    context = {
        'days': days,
        'total_revenue': total_revenue,
        'total_orders_count': total_orders_count,
        'avg_order_value': avg_order_value,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'sales_by_status': list(sales_by_status),
        'top_products': top_products,
    }
    return render(request, 'reports/dashboard.html', context)

@staff_member_required
def export_sales_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Customer', 'Email', 'Total Price', 'Status', 'Payment Method', 'Date'])
    
    orders = Order.objects.all().order_by('-created_at')
    for order in orders:
        writer.writerow([order.id, order.full_name, order.email, order.total_price, order.get_status_display(), order.get_payment_method_display(), order.created_at.strftime('%Y-%m-%d %H:%M')])
        
    return response

@staff_member_required
def export_sales_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Sales Report"
    
    # Headers
    headers = ['Order ID', 'Customer', 'Email', 'Total Price', 'Status', 'Payment Method', 'Date']
    ws.append(headers)
    
    # Styling headers
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
        
    orders = Order.objects.all().order_by('-created_at')
    for order in orders:
        ws.append([
            order.id, 
            order.full_name, 
            order.email, 
            float(order.total_price), 
            order.get_status_display(), 
            order.get_payment_method_display(), 
            order.created_at.strftime('%Y-%m-%d %H:%M')
        ])
        
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="sales_report.xlsx"'
    wb.save(response)
    return response
