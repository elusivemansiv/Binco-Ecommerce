from .models import Cart, Category, ShippingConfig


def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.items.count()
        except Cart.DoesNotExist:
            count = 0
    return {'cart_count': count}


def categories(request):
    return {'all_categories': Category.objects.all()}


def shipping_config(request):
    return {'shipping_conf': ShippingConfig.get_config()}
