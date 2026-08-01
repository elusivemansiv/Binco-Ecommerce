from django.db import models
from django.contrib.auth.models import User

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField('catalog.Product', blank=True)

    class Meta:
        db_table = 'store_wishlist'

    def __str__(self):
        return f"Wishlist of {self.user.username}"
