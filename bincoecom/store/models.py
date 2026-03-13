from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=100, blank=True, help_text='FontAwesome class e.g. fa-laptop')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50, blank=True, null=True, help_text="Hex code e.g. #FFFFFF")

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    colors = models.ManyToManyField(Color, blank=True)
    sizes = models.ManyToManyField(Size, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.IntegerField(default=0, help_text="Total stock if no variations, otherwise managed by variations")
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def discount_percent(self):
        if self.discount_price and self.price > 0:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

    @property
    def effective_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    @property
    def total_stock(self):
        variations = self.variations.all()
        if variations.exists():
            return sum(v.stock for v in variations)
        return self.stock

    def get_image_for_color(self, color_name):
        if color_name:
            color_img = self.extra_images.filter(color__name=color_name).first()
            if color_img:
                return color_img.image
        return self.image

    def __str__(self):
        return self.name


class ProductVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'color', 'size')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Sync parent product stock
        product = self.product
        total = sum(v.stock for v in product.variations.all())
        Product.objects.filter(id=product.id).update(stock=total)

    def __str__(self):
        color_name = self.color.name if self.color else "N/A"
        size_name = self.size.name if self.size else "N/A"
        return f"{self.product.name} - {color_name} - {size_name}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='extra_images')
    image = models.ImageField(upload_to='products/gallery/')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True, related_name='images')

    def __str__(self):
        return f"Image for {self.product.name} ({self.color.name if self.color else 'No Color'})"


class ProductReview(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.username} – {self.product.name} ({self.rating}★)"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)

    @property
    def subtotal(self):
        return self.product.effective_price * self.quantity

    @property
    def selected_image(self):
        return self.product.get_image_for_color(self.color)

    def __str__(self):
        return f"{self.quantity}× {self.product.name}"


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField(default=10)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    max_uses = models.PositiveIntegerField(default=100)
    used_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.code} ({self.discount_percent}%)"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('mobile', 'Mobile Banking'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_status = self.status

    def save(self, *args, **kwargs):
        if self.pk:
            # If the status is changing to cancelled
            if self.status == 'cancelled' and self._original_status != 'cancelled':
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

            # If the status is changing from cancelled back to something else (uncancelled)
            elif self._original_status == 'cancelled' and self.status != 'cancelled':
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
        self._original_status = self.status

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    @property
    def final_total(self):
        return self.total_price - self.discount_amount


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)

    @property
    def subtotal(self):
        return self.price * self.quantity

    @property
    def selected_image(self):
        if self.product:
            return self.product.get_image_for_color(self.color)
        return None

    def __str__(self):
        return f"{self.quantity}× {self.product_name}"


class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return f"Wishlist of {self.user.username}"


class HomeSlider(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to='sliders/')
    link_url = models.CharField(max_length=500, default='/')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class PromotionCard(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to='promotions/')
    link_url = models.CharField(max_length=500, default='/')
    badge_text = models.CharField(max_length=50, blank=True, help_text="e.g. NEW, -20%, HOT")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title