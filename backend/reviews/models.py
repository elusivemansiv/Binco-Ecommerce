from django.db import models
from django.contrib.auth.models import User

class ProductReview(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')
        db_table = 'store_productreview'

    def __str__(self):
        return f"{self.user.username} – {self.product.name} ({self.rating}★)"
