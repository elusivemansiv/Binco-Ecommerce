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
        db_table = 'store_category'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50, blank=True, null=True, help_text="Hex code e.g. #FFFFFF")

    class Meta:
        db_table = 'store_color'

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'store_size'

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

    class Meta:
        db_table = 'store_product'

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
        db_table = 'store_productvariation'

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

    class Meta:
        db_table = 'store_productimage'

    def __str__(self):
        return f"Image for {self.product.name} ({self.color.name if self.color else 'No Color'})"
