from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('return_requested', 'Return Requested'),
        ('return_approved', 'Return Approved'),
        ('returned', 'Successfully Returned'),
    ]
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('mobile', 'Mobile Banking'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    coupon = models.ForeignKey('cart.Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Total price of items before discount and shipping")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    return_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_order'

    @property
    def get_items_total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def get_final_total(self):
        return self.total_price - self.discount_amount + self.shipping_charge

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_status = self.status

    def save(self, *args, **kwargs):
        from catalog.models import ProductVariation, Product

        if self.pk:
            # If the status is changing to cancelled or returned
            if self.status in ['cancelled', 'returned'] and self._original_status not in ['cancelled', 'returned']:
                for item in self.items.all():
                    if item.product:
                        # Restore stock to variation if it exists
                        variation = ProductVariation.objects.filter(
                            product=item.product,
                            color__name=item.color if item.color else None,
                            size__name=item.size if item.size else None
                        ).first()
                        if variation:
                            variation.stock += item.quantity
                            variation.save(update_fields=['stock'])
                        else:
                            item.product.stock += item.quantity
                            item.product.save(update_fields=['stock'])

            # If the status is changing from cancelled/returned back to something else (uncancelled/unreturned)
            elif self._original_status in ['cancelled', 'returned'] and self.status not in ['cancelled', 'returned']:
                for item in self.items.all():
                    if item.product:
                        variation = ProductVariation.objects.filter(
                            product=item.product,
                            color__name=item.color if item.color else None,
                            size__name=item.size if item.size else None
                        ).first()
                        if variation:
                            variation.stock -= item.quantity
                            if variation.stock < 0:
                                variation.stock = 0
                            variation.save(update_fields=['stock'])
                        else:
                            item.product.stock -= item.quantity
                            if item.product.stock < 0:
                                item.product.stock = 0
                            item.product.save(update_fields=['stock'])
                        
        super().save(*args, **kwargs)

        # Fire notification on status change
        if self.pk and self.status != self._original_status:
            try:
                from notifications.services import NotificationService
                NotificationService.notify_order_status_change(self)
            except Exception:
                pass  # Don't let notification failure break order saving

        self._original_status = self.status

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    @property
    def final_total(self):
        return self.total_price - self.discount_amount


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalog.Product', on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'store_orderitem'

    @property
    def subtotal(self):
        if self.price is None or self.quantity is None:
            return 0
        return self.price * self.quantity

    @property
    def selected_image(self):
        if self.product:
            return self.product.get_image_for_color(self.color)
        return None

    def __str__(self):
        return f"{self.quantity}× {self.product_name}"



