from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # OpenAPI Docs
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # App API routes
    path('', include('accounts.api.urls')),
    path('', include('catalog.api.urls')),
    path('', include('cart.api.urls')),
    path('', include('orders.api.urls')),
    path('', include('reviews.api.urls')),
    path('', include('wishlist.api.urls')),
    path('', include('cms.api.urls')),
    path('', include('notifications.api.urls')),
    path('seller/', include('seller.api.urls')),
    path('', include('siteconfig.api.urls')),
]
