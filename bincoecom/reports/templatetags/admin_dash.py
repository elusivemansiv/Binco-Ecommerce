from django import template
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from store.models import Order, Product, OrderItem
import json

register = template.Library()

@register.simple_tag
def get_admin_dashboard_data():
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    
    # Basic Stats
    total_orders = Order.objects.count()
    recent_orders = Order.objects.filter(created_at__gte=thirty_days_ago).count()
    
    # Calculate revenue
    total_revenue = sum(order.final_total for order in Order.objects.filter(status='delivered'))
    recent_revenue = sum(order.final_total for order in Order.objects.filter(status='delivered', created_at__gte=thirty_days_ago))
    
    total_products = Product.objects.count()
    total_customers = Order.objects.values('user').distinct().count()
    
    # Today's Sales
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    sales_today = sum(o.final_total for o in Order.objects.filter(created_at__gte=today_start, status='delivered'))
    orders_today = Order.objects.filter(created_at__gte=today_start).count()
    
    # Pending Tasks
    pending_orders_count = Order.objects.filter(status='pending').count()
    
    # Best Selling Products
    best_sellers = Product.objects.annotate(
        total_sold=Sum('orderitem__quantity')
    ).filter(total_sold__gt=0).order_by('-total_sold')[:5]
    
    # Category Distribution
    from store.models import Category
    top_categories = Category.objects.annotate(
        product_count=Count('products'),
        total_sales=Sum('products__orderitem__quantity')
    ).filter(total_sales__gt=0).order_by('-total_sales')[:5]
    
    # Recent Orders
    latest_orders = Order.objects.all().order_by('-created_at')[:8]
    
    # Sales last 7 days for the graph
    seven_days_ago = now - timedelta(days=7)
    labels = []
    data = []
    
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        day_orders = Order.objects.filter(created_at__range=(day_start, day_end))
        day_revenue = sum(o.final_total for o in day_orders if o.status == 'delivered')
        labels.append(day.strftime('%b %d'))
        data.append(float(day_revenue))
        
    return {
        'total_orders': total_orders,
        'recent_orders': recent_orders,
        'total_revenue': total_revenue,
        'recent_revenue': recent_revenue,
        'total_products': total_products,
        'total_customers': total_customers,
        'sales_today': sales_today,
        'orders_today': orders_today,
        'pending_orders_count': pending_orders_count,
        'best_sellers': best_sellers,
        'top_categories': top_categories,
        'latest_orders': latest_orders,
        'chart_labels': json.dumps(labels),
        'chart_data': json.dumps(data),
    }
