from cart.models import Cart
from catalog.models import Category
from store.models import ShippingConfig


from wishlist.models import Wishlist

def cart_count(request):
    count = 0
    total = 0.00
    cart_items = []
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.prefetch_related('items__product').get(user=request.user)
            count = cart.items.count()
            total = cart.total
            cart_items = cart.items.all()
        except Cart.DoesNotExist:
            count = 0
    return {'cart_count': count, 'cart_total': total, 'header_cart_items': cart_items}

def wishlist_count(request):
    count = 0
    wishlist_products = []
    if request.user.is_authenticated:
        try:
            wishlist = Wishlist.objects.prefetch_related('products').get(user=request.user)
            count = wishlist.products.count()
            wishlist_products = wishlist.products.all()
        except Wishlist.DoesNotExist:
            count = 0
    return {'wishlist_count': count, 'header_wishlist_products': wishlist_products}


def categories(request):
    return {'all_categories': Category.objects.all()}


def shipping_config(request):
    return {'shipping_conf': ShippingConfig.get_config()}
