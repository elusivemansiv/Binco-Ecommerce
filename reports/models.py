from django.db import models

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('marketing', 'Marketing & Advertising'),
        ('inventory', 'Inventory Purchase'),
        ('shipping', 'Shipping & Logistics'),
        ('salaries', 'Salaries & Wages'),
        ('utilities', 'Utilities & Rent'),
        ('other', 'Other Operating Expenses'),
    ]

    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} - ৳{self.amount} ({self.date})"
