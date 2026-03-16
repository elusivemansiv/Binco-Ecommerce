from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Sum, Count, F
from datetime import timedelta
from .models import (
    Product, Category, Cart, CartItem, Order, OrderItem,
    Wishlist, Coupon, ProductReview, ProductImage,
    HomeSlider, PromotionCard, ProductVariation, Color, Size, ShippingConfig
)


# ─────────────────────────── HOME ────────────────────────────
def home(request):
    all_categories = Category.objects.all()
    featured = Product.objects.filter(is_featured=True, is_active=True)[:8]
    deals = Product.objects.filter(discount_price__isnull=False, is_active=True)[:8]
    trending = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    sliders = HomeSlider.objects.filter(is_active=True)
    promotions = PromotionCard.objects.filter(is_active=True)

    context = {
        'all_categories': all_categories,
        'featured': featured,
        'deals': deals,
        'trending': trending,
        'sliders': sliders,
        'promotions': promotions,
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
        
        # --- Related Products for Cart ---
        cart_categories = items.values_list('product__category', flat=True).distinct()
        related_products = Product.objects.filter(
            category__in=cart_categories, 
            is_active=True
        ).exclude(id__in=items.values_list('product_id', flat=True))[:4]
        
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

        shipping_conf = ShippingConfig.get_config()
        shipping_charge = shipping_conf.shipping_charge if cart.total < shipping_conf.free_shipping_threshold else 0

        context = {
            'cart': cart,
            'items': items,
            'related_products': related_products,
            'discount_percent': discount_percent,
            'discount_amount': discount_amount,
            'shipping_charge': shipping_charge,
            'final_total': cart.total - discount_amount + shipping_charge,
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

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true'

    # --- Variation Stock Check ---
    from .models import ProductVariation
    variation = ProductVariation.objects.filter(
        product=product,
        color__name=color_name if color_name else None,
        size__name=size_name if size_name else None
    ).first()

    if variation:
        if variation.stock < 1:
            msg = f'Sorry, this variant ({color_name} - {size_name}) is out of stock.'
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': msg})
            messages.error(request, msg)
            return redirect('product_detail', product_id=product.id)
    elif product.variations.exists():
        msg = 'Please select a valid color and size.'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': msg})
        messages.error(request, msg)
        return redirect('product_detail', product_id=product.id)
    elif product.stock < 1:
        msg = f'Sorry, "{product.name}" is out of stock.'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': msg})
        messages.error(request, msg)
        return redirect('product_detail', product_id=product.id)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product, color=color_name, size=size_name)
    if not created:
        item.quantity += 1
        item.save()
    
    cart_count = cart.items.count()
    success_msg = f'"{product.name}" added to cart!'
    
    if is_ajax:
        from django.http import JsonResponse
        return JsonResponse({
            'status': 'success', 
            'message': success_msg,
            'cart_count': cart_count
        })

    messages.success(request, success_msg)
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

    shipping_conf = ShippingConfig.get_config()
    shipping_charge = shipping_conf.shipping_charge if cart.total < shipping_conf.free_shipping_threshold else 0
    final_total = cart.total - discount_amount + shipping_charge

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
        'shipping_charge': shipping_charge,
        'final_total': final_total,
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


@login_required(login_url='login')
def request_return(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        if order.status not in ['shipped', 'delivered']:
            messages.error(request, "Only shipped or delivered orders can be returned.")
            return redirect('order_detail', order_id=order.id)
            
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, "Please provide a reason for the return.")
            return redirect('order_detail', order_id=order.id)
            
        order.status = 'return_requested'
        order.return_reason = reason
        order.save()
        
        messages.success(request, "Return request submitted successfully. The seller will review it soon.")
        return redirect('order_detail', order_id=order.id)
    
    return redirect('order_history')


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


@login_required(login_url='login')
def seller_dashboard(request):
    if not request.user.profile.is_seller:
        messages.error(request, 'You need to be a seller to access this page.')
        return redirect('dashboard')
    
    products = Product.objects.filter(seller=request.user)
    
    # Base query for orders containing seller's items
    seller_items = OrderItem.objects.filter(product__seller=request.user)
    
    # Status-specific metrics (Unique orders)
    active_orders = seller_items.exclude(order__status__in=['delivered', 'cancelled', 'returned']).values('order').distinct().count()
    success_orders = seller_items.filter(order__status='delivered').values('order').distinct().count()
    cancelled_orders = seller_items.filter(order__status='cancelled').values('order').distinct().count()
    returned_orders = seller_items.filter(order__status='returned').values('order').distinct().count()
    
    # Total Earnings (Delivered orders only)
    total_earnings = seller_items.filter(order__status='delivered').aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0
    
    # Graph Data (Last 30 days)
    labels = []
    earnings_series = []
    orders_series = []
    
    today = timezone.now().date()
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        labels.append(day.strftime('%b %d'))
        
        # Daily earnings
        daily_earnings = seller_items.filter(
            order__status='delivered', 
            order__created_at__date=day
        ).aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0
        earnings_series.append(float(daily_earnings))
        
        # Daily orders count
        daily_orders = seller_items.filter(
            order__created_at__date=day
        ).values('order').distinct().count()
        orders_series.append(daily_orders)

    context = {
        'products_count': products.count(), 
        'orders_count': seller_items.values('order').distinct().count(),
        'active_orders': active_orders,
        'success_orders': success_orders,
        'cancelled_orders': cancelled_orders,
        'returned_orders': returned_orders,
        'total_earnings': total_earnings,
        'labels': labels,
        'earnings_series': earnings_series,
        'orders_series': orders_series,
    }
    return render(request, 'store/seller_dashboard.html', context)


@login_required(login_url='login')
def seller_products(request):
    if not request.user.profile.is_seller:
        return redirect('dashboard')
    
    products = Product.objects.filter(seller=request.user)
    context = {'products': products}
    return render(request, 'store/seller_products.html', context)


@login_required(login_url='login')
def seller_orders(request):
    if not request.user.profile.is_seller:
        return redirect('dashboard')
    
    status_filter = request.GET.get('status')
    
    # Fetch orders that contain items belonging to this seller
    seller_items = OrderItem.objects.filter(product__seller=request.user).select_related('order', 'product', 'order__user').prefetch_related('product__extra_images')
    
    if status_filter:
        if status_filter == 'success':
            seller_items = seller_items.filter(order__status='delivered')
        elif status_filter == 'cancelled':
            seller_items = seller_items.filter(order__status='cancelled')
        elif status_filter == 'returned':
            seller_items = seller_items.filter(order__status='returned')
        elif status_filter == 'active':
            seller_items = seller_items.exclude(order__status__in=['delivered', 'cancelled', 'returned'])

    # Group by order for the template
    orders_dict = {}
    for item in seller_items:
        if item.order.id not in orders_dict:
            orders_dict[item.order.id] = {
                'order': item.order,
                'items': [],
                'seller_total': 0
            }
        orders_dict[item.order.id]['items'].append(item)
        orders_dict[item.order.id]['seller_total'] += item.subtotal
        
    context = {
        'orders': orders_dict.values(),
        'current_status': status_filter
    }
    return render(request, 'store/seller_orders.html', context)


from .forms import ProductForm, ProductVariationFormSet, ProductImageFormSet

@login_required(login_url='login')
def add_product(request):
    if not request.user.profile.is_seller:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        variation_formset = ProductVariationFormSet(request.POST, prefix='variations')
        image_formset = ProductImageFormSet(request.POST, request.FILES, prefix='images')
        
        if form.is_valid() and variation_formset.is_valid() and image_formset.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            
            # Save variations
            variations = variation_formset.save(commit=False)
            for variation in variations:
                variation.product = product
                variation.save()
            
            # Save images
            images = image_formset.save(commit=False)
            for image in images:
                image.product = product
                image.save()
            
            # Handle deletions
            for obj in variation_formset.deleted_objects:
                obj.delete()
            for obj in image_formset.deleted_objects:
                obj.delete()

            messages.success(request, 'Product listed successfully!')
            return redirect('seller_dashboard')
    else:
        form = ProductForm()
        variation_formset = ProductVariationFormSet(prefix='variations')
        image_formset = ProductImageFormSet(prefix='images')
    
    context = {
        'form': form,
        'variation_formset': variation_formset,
        'image_formset': image_formset,
        'action': 'Add'
    }
    return render(request, 'store/product_form.html', context)


@login_required(login_url='login')
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        variation_formset = ProductVariationFormSet(request.POST, instance=product, prefix='variations')
        image_formset = ProductImageFormSet(request.POST, request.FILES, instance=product, prefix='images')
        
        if form.is_valid() and variation_formset.is_valid() and image_formset.is_valid():
            product = form.save()
            variation_formset.save()
            image_formset.save()
            
            # Update slug
            product.slug = ''  # force regeneration
            product.save()
            
            messages.success(request, 'Product updated!')
            return redirect('seller_dashboard')
    else:
        form = ProductForm(instance=product)
        variation_formset = ProductVariationFormSet(instance=product, prefix='variations')
        image_formset = ProductImageFormSet(instance=product, prefix='images')
    
    context = {
        'form': form,
        'variation_formset': variation_formset,
        'image_formset': image_formset,
        'product': product,
        'action': 'Edit'
    }
    return render(request, 'store/product_form.html', context)


@login_required(login_url='login')
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    product.delete()
    messages.success(request, 'Product deleted.')
    return redirect('seller_dashboard')


@login_required(login_url='login')
def ajax_add_color(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip() or '#000000'
        if name:
            color, created = Color.objects.get_or_create(name__iexact=name, defaults={'name': name, 'code': code})
            return JsonResponse({'status': 'success', 'id': color.id, 'name': color.name})
    return JsonResponse({'status': 'error', 'message': 'Invalid data'})


@login_required(login_url='login')
def update_order_status(request, order_id):
    if not request.user.profile.is_seller:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        allowed_statuses = ['pending', 'processing', 'cancelled', 'return_approved']
        
        if new_status not in allowed_statuses:
            return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)
        
        order = get_object_or_404(Order, id=order_id)
        
        # Verify this order contains items from this seller
        has_seller_items = OrderItem.objects.filter(order=order, product__seller=request.user).exists()
        if not has_seller_items:
            return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
        
        # Logic for status transitions
        if order.status in ['pending', 'processing']:
            if new_status not in ['pending', 'processing', 'cancelled']:
                return JsonResponse({'status': 'error', 'message': 'Invalid status transition'}, status=400)
        elif order.status == 'return_requested':
            if new_status not in ['return_requested', 'return_approved']:
                return JsonResponse({'status': 'error', 'message': 'Sellers can only approve or keep return requested status'}, status=400)
        else:
            return JsonResponse({'status': 'error', 'message': 'Order is in a state handled by Admin and cannot be changed by Seller'}, status=400)

        order.status = new_status
        order.save()
        
        return JsonResponse({
            'status': 'success', 
            'new_status': order.status, 
            'display_status': order.get_status_display()
        })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required(login_url='login')
def ajax_add_size(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            size, created = Size.objects.get_or_create(name__iexact=name, defaults={'name': name})
            return JsonResponse({'status': 'success', 'id': size.id, 'name': size.name})
    return JsonResponse({'status': 'error', 'message': 'Invalid data'})