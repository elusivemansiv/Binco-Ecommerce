from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import (
    Product, Category, Cart, CartItem, Order, OrderItem,
    Wishlist, Coupon, ProductReview, ProductImage
)


# ─────────────────────────── HOME ────────────────────────────
def home(request):
    categories = Category.objects.all()
    featured = Product.objects.filter(is_featured=True, is_active=True)[:8]
    deals = Product.objects.filter(discount_price__isnull=False, is_active=True)[:8]
    trending = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    context = {
        'categories': categories,
        'featured': featured,
        'deals': deals,
        'trending': trending,
    }
    return render(request, 'store/home.html', context)


# ─────────────────────────── PRODUCT LIST ────────────────────
def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()

    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort = request.GET.get('sort', 'newest')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'oldest':
        products = products.order_by('created_at')
    else:
        products = products.order_by('-created_at')

    selected_category = None
    if category_slug:
        selected_category = Category.objects.filter(slug=category_slug).first()

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': selected_category,
        'category_slug': category_slug,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
    }
    return render(request, 'store/product_list.html', context)


# ─────────────────────────── PRODUCT DETAIL ──────────────────
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    extra_images = product.extra_images.all()
    reviews = product.reviews.all().order_by('-created_at')
    related = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]

    user_reviewed = False
    if request.user.is_authenticated:
        user_reviewed = reviews.filter(user=request.user).exists()

    context = {
        'product': product,
        'extra_images': extra_images,
        'reviews': reviews,
        'related': related,
        'user_reviewed': user_reviewed,
        'variations': product.variations.all(),
    }
    return render(request, 'store/product_detail.html', context)


# ─────────────────────────── REVIEWS ─────────────────────────
@login_required(login_url='login')
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        ProductReview.objects.update_or_create(
            product=product, user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )
        messages.success(request, 'Review submitted!')
    return redirect('product_detail', product_id=product_id)


# ─────────────────────────── CART ────────────────────────────
def _get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart
    return None


def cart_view(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.select_related('product').all()
        coupon = request.session.get('coupon_code')
        discount_percent = 0
        discount_amount = 0
        coupon_obj = None
        if coupon:
            try:
                now = timezone.now()
                coupon_obj = Coupon.objects.get(
                    code=coupon, is_active=True,
                    valid_from__lte=now, valid_to__gte=now
                )
                discount_percent = coupon_obj.discount_percent
                discount_amount = cart.total * discount_percent / 100
            except Coupon.DoesNotExist:
                request.session.pop('coupon_code', None)

        context = {
            'cart': cart,
            'items': items,
            'discount_percent': discount_percent,
            'discount_amount': discount_amount,
            'final_total': cart.total - discount_amount,
            'coupon_code': coupon,
        }
        return render(request, 'store/cart.html', context)
    else:
        # Session-based cart for anonymous users
        session_cart = request.session.get('cart', {})
        items = []
        total = 0
        for pid, qty in session_cart.items():
            try:
                product = Product.objects.get(id=pid)
                subtotal = product.effective_price * qty
                total += subtotal
                items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})
            except Product.DoesNotExist:
                pass
        return render(request, 'store/cart.html', {'items': items, 'cart': None, 'final_total': total, 'discount_amount': 0})


@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    color_name = ''
    size_name = ''
    if request.method == 'POST':
        color_name = request.POST.get('color', '')
        size_name = request.POST.get('size', '')

    # --- Variation Stock Check ---
    from .models import ProductVariation
    variation = ProductVariation.objects.filter(
        product=product,
        color__name=color_name if color_name else None,
        size__name=size_name if size_name else None
    ).first()

    if variation:
        if variation.stock < 1:
            messages.error(request, f'Sorry, this variant ({color_name} - {size_name}) is out of stock.')
            return redirect('product_detail', product_id=product.id)
    elif product.variations.exists():
        # If product has variations but none found/selected correctly
        messages.error(request, 'Please select a valid color and size.')
        return redirect('product_detail', product_id=product.id)
    elif product.stock < 1:
        messages.error(request, f'Sorry, "{product.name}" is out of stock.')
        return redirect('product_detail', product_id=product.id)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product, color=color_name, size=size_name)
    if not created:
        item.quantity += 1
        item.save()
    messages.success(request, f'"{product.name}" added to cart!')
    return redirect('cart')


@login_required(login_url='login')
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    qty = int(request.POST.get('quantity', 1))
    
    # Optional: Add stock validation on update
    from .models import ProductVariation
    variation = ProductVariation.objects.filter(
        product=item.product,
        color__name=item.color if item.color else None,
        size__name=item.size if item.size else None
    ).first()
    
    current_stock = variation.stock if variation else item.product.stock
    
    if qty > current_stock:
        messages.error(request, f'Only {current_stock} items available.')
        return redirect('cart')

    if qty <= 0:
        item.delete()
        messages.info(request, 'Item removed from cart.')
    else:
        item.quantity = qty
        item.save()
    return redirect('cart')


@login_required(login_url='login')
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.info(request, 'Item removed from cart.')
    return redirect('cart')


@login_required(login_url='login')
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code', '').strip().upper()
        try:
            now = timezone.now()
            coupon = Coupon.objects.get(code=code, is_active=True, valid_from__lte=now, valid_to__gte=now)
            request.session['coupon_code'] = code
            messages.success(request, f'Coupon "{code}" applied – {coupon.discount_percent}% off!')
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid or expired coupon code.')
    return redirect('cart')


@login_required(login_url='login')
def remove_coupon(request):
    request.session.pop('coupon_code', None)
    messages.info(request, 'Coupon removed.')
    return redirect('cart')


# ─────────────────────────── CHECKOUT ────────────────────────
@login_required(login_url='login')
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()
    if not items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    coupon_code = request.session.get('coupon_code')
    discount_percent = 0
    discount_amount = 0
    coupon_obj = None
    if coupon_code:
        try:
            now = timezone.now()
            coupon_obj = Coupon.objects.get(
                code=coupon_code, is_active=True,
                valid_from__lte=now, valid_to__gte=now
            )
            discount_percent = coupon_obj.discount_percent
            discount_amount = cart.total * discount_percent / 100
        except Coupon.DoesNotExist:
            pass

    if request.method == 'POST':
        # --- Stock validation ---
        from .models import ProductVariation
        for item in items:
            variation = ProductVariation.objects.filter(
                product=item.product,
                color__name=item.color if item.color else None,
                size__name=item.size if item.size else None
            ).first()
            
            stock_available = variation.stock if variation else item.product.stock
            
            if stock_available < item.quantity:
                messages.error(request, f'Sorry, "{item.product.name}" variant only has {stock_available} left in stock (you requested {item.quantity}).')
                return redirect('cart')

        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        payment_method = request.POST.get('payment_method', 'cod')

        if not all([full_name, email, phone, address, city]):
            messages.error(request, 'Please fill in all required fields (Name, Email, Phone, Address, City).')
            return redirect('checkout')

        if payment_method != 'cod':
            messages.error(request, 'Currently, only Cash on Delivery is processable. Other options will be implemented later.')
            return redirect('checkout')

        order = Order.objects.create(
            user=request.user,
            coupon=coupon_obj,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            postal_code=postal_code,
            total_price=cart.total,
            discount_amount=discount_amount,
            payment_method=payment_method,
        )
        for item in items:
            # Decrease stock
            variation = ProductVariation.objects.filter(
                product=item.product,
                color__name=item.color if item.color else None,
                size__name=item.size if item.size else None
            ).first()
            
            if variation:
                variation.stock -= item.quantity
                variation.save(update_fields=['stock'])
            else:
                item.product.stock -= item.quantity
                item.product.save(update_fields=['stock'])
            
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                price=item.product.effective_price,
                quantity=item.quantity,
                color=item.color,
                size=item.size,
            )

        if coupon_obj:
            coupon_obj.used_count += 1
            coupon_obj.save()
        items.delete()
        request.session.pop('coupon_code', None)
        messages.success(request, 'Order placed successfully!')
        return redirect('order_success', order_id=order.id)

    profile = request.user.profile
    context = {
        'cart': cart,
        'items': items,
        'total': cart.total,
        'discount_amount': discount_amount,
        'final_total': cart.total - discount_amount,
        'profile': profile,
    }
    return render(request, 'store/checkout.html', context)


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})


@login_required(login_url='login')
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/orders.html', {'orders': orders})


@login_required(login_url='login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


# ─────────────────────────── WISHLIST ────────────────────────
@login_required(login_url='login')
def wishlist_view(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'store/wishlist.html', {'wishlist': wishlist})


@login_required(login_url='login')
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    if product in wishlist.products.all():
        wishlist.products.remove(product)
        messages.info(request, f'"{product.name}" removed from wishlist.')
    else:
        wishlist.products.add(product)
        messages.success(request, f'"{product.name}" added to wishlist!')
    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))


# ─────────────────────────── SELLER DASHBOARD ────────────────
@login_required(login_url='login')
def seller_dashboard(request):
    if not request.user.profile.is_seller:
        messages.error(request, 'You need to be a seller to access this page.')
        return redirect('dashboard')
    products = Product.objects.filter(seller=request.user)
    orders_count = OrderItem.objects.filter(product__seller=request.user).values('order').distinct().count()
    context = {'products': products, 'orders_count': orders_count}
    return render(request, 'store/seller_dashboard.html', context)


@login_required(login_url='login')
def add_product(request):
    if not request.user.profile.is_seller:
        return redirect('dashboard')
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        discount_price = request.POST.get('discount_price') or None
        stock = request.POST.get('stock', 0)
        category_id = request.POST.get('category')
        image = request.FILES.get('image')
        is_featured = request.POST.get('is_featured') == 'on'

        category = Category.objects.filter(id=category_id).first()
        product = Product.objects.create(
            seller=request.user,
            category=category,
            name=name,
            description=description,
            price=price,
            discount_price=discount_price,
            stock=stock,
            image=image,
            is_featured=is_featured,
        )
        # Extra images
        for img in request.FILES.getlist('extra_images'):
            ProductImage.objects.create(product=product, image=img)

        messages.success(request, 'Product listed successfully!')
        return redirect('seller_dashboard')
    return render(request, 'store/product_form.html', {'categories': categories, 'action': 'Add'})


@login_required(login_url='login')
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    categories = Category.objects.all()
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.discount_price = request.POST.get('discount_price') or None
        product.stock = request.POST.get('stock', 0)
        category_id = request.POST.get('category')
        product.category = Category.objects.filter(id=category_id).first()
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
        product.is_featured = request.POST.get('is_featured') == 'on'
        product.slug = ''  # force regeneration
        product.save()
        messages.success(request, 'Product updated!')
        return redirect('seller_dashboard')
    return render(request, 'store/product_form.html', {'categories': categories, 'product': product, 'action': 'Edit'})


@login_required(login_url='login')
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    product.delete()
    messages.success(request, 'Product deleted.')
    return redirect('seller_dashboard')