from django.contrib import admin
from .models import ShippingConfig

@admin.register(ShippingConfig)
class ShippingConfigAdmin(admin.ModelAdmin):
    list_display = ('shipping_charge', 'free_shipping_threshold', 'is_active', 'updated_at')
    
    def has_add_permission(self, request):
        # Prevent adding more than one config
        return not ShippingConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting the config
        return False
