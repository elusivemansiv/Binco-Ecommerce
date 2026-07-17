from django import template
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from orders.models import Order, OrderItem
from catalog.models import Product, Category
from django.contrib.auth.models import User
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
    total_customers = User.objects.filter(is_staff=False).count()
    
    # Today's Sales
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    sales_today = sum(o.final_total for o in Order.objects.filter(created_at__gte=today_start, status='delivered'))
    orders_today = Order.objects.filter(created_at__gte=today_start).count()
    
    # Pending Tasks
    pending_orders_count = Order.objects.filter(status='pending').count()
    
    # Total items sold
    total_sales_count = OrderItem.objects.aggregate(total=Sum('quantity'))['total'] or 0
    
    # Best Selling Products (with image)
    best_sellers = Product.objects.annotate(
        total_sold=Sum('orderitem__quantity'),
        total_earning=Sum('orderitem__price')
    ).filter(total_sold__gt=0).order_by('-total_sold')[:5]
    
    # Build best sellers data with image URLs
    best_sellers_data = []
    for p in best_sellers:
        img_url = p.image.url if p.image else ''
        earning = 0
        # Calculate actual earnings
        items = OrderItem.objects.filter(product=p)
        for item in items:
            if item.price and item.quantity:
                earning += item.price * item.quantity
        best_sellers_data.append({
            'name': p.name,
            'image_url': img_url,
            'price': float(p.price),
            'created_at': p.created_at,
            'total_sold': p.total_sold or 0,
            'total_earning': float(earning),
        })
    
    # Category Distribution
    top_categories = Category.objects.annotate(
        product_count=Count('products'),
        total_sales=Sum('products__orderitem__quantity')
    ).filter(total_sales__gt=0).order_by('-total_sales')[:5]
    
    # Customer analytics
    new_customers = User.objects.filter(is_staff=False, date_joined__gte=thirty_days_ago).count()
    returning_customers = total_customers - new_customers if total_customers > new_customers else 0
    
    # Recent Orders
    latest_orders = Order.objects.all().order_by('-created_at')[:8]
    
    # Sales last 7 days for the graph
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
        'total_sales_count': total_sales_count,
        'best_sellers': best_sellers,
        'best_sellers_data': best_sellers_data,
        'top_categories': top_categories,
        'latest_orders': latest_orders,
        'new_customers': new_customers,
        'returning_customers': returning_customers,
        'chart_labels': json.dumps(labels),
        'chart_data': json.dumps(data),
    }
