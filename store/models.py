from django.db import models

class ShippingConfig(models.Model):
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=999.00)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Shipping Configuration'
        verbose_name_plural = 'Shipping Configuration'
        db_table = 'store_shippingconfig'

    def save(self, *args, **kwargs):
        # We ensure only one instance exists
        if not self.pk and ShippingConfig.objects.exists():
            return
        super().save(*args, **kwargs)

    @classmethod
    def get_config(cls):
        config, created = cls.objects.get_or_create(id=1)
        return config

    def __str__(self):
        return f"Shipping: ৳{self.shipping_charge} | Free over: ৳{self.free_shipping_threshold}"