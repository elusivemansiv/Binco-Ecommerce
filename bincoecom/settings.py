from django.utils.safestring import mark_safe
"""
Django settings for bincoecom project.
"""

import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-kht%m#0a5_a1x8v$0=&uvs6ii)*er!iy6(d_z*b@4rpr(6c7fh')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['bincoecom.stradigtech.com', 'www.bincoecom.stradigtech.com', 'localhost', '127.0.0.1']

CSRF_TRUSTED_ORIGINS = ['https://*.up.railway.app']

INSTALLED_APPS = [
    'jet.dashboard',
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',
    'catalog',
    'cart',
    'orders',
    'reviews',
    'wishlist',
    'seller',
    'accounts',
    'cms',
    'reports',
    'siteconfig',
    'notifications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bincoecom.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.cart_count',
                'store.context_processors.wishlist_count',
                'store.context_processors.categories',
                'store.context_processors.shipping_config',
                'siteconfig.context_processors.site_settings',
                'notifications.context_processors.notification_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'bincoecom.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

db_from_env = dj_database_url.config(conn_max_age=500)
if db_from_env:
    DATABASES['default'].update(db_from_env)

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

# ---------------------------------
# Django Jet Reboot Configuration
# ---------------------------------
JET_DEFAULT_THEME = 'default'
JET_SIDE_MENU_COMPACT = True
JET_CHANGE_FORM_SIBLING_LINKS = True

JET_SIDE_MENU_ITEMS = [
    {'label': 'Catalog', 'app_label': 'catalog', 'items': [
        {'name': 'catalog.product', 'label': 'Products'},
        {'name': 'catalog.category', 'label': 'Categories'},
        {'name': 'catalog.color', 'label': 'Colors'},
        {'name': 'catalog.size', 'label': 'Sizes'},
    ]},
    {'label': 'Orders', 'app_label': 'orders', 'items': [
        {'name': 'orders.order', 'label': 'Orders'},
    ]},
    {'label': 'Cart & Coupons', 'app_label': 'cart', 'items': [
        {'name': 'cart.cart', 'label': 'Carts'},
        {'name': 'cart.coupon', 'label': 'Coupons'},
    ]},
    {'label': 'Reviews', 'app_label': 'reviews', 'items': [
        {'name': 'reviews.productreview', 'label': 'Product Reviews'},
    ]},
    {'label': 'Wishlist', 'app_label': 'wishlist', 'items': [
        {'name': 'wishlist.wishlist', 'label': 'Wishlists'},
    ]},
    {'label': 'Store Settings', 'app_label': 'store', 'items': [
        {'name': 'store.shippingconfig', 'label': 'Shipping Settings'},
    ]},
    {'label': 'Accounts', 'app_label': 'auth', 'items': [
        {'name': 'auth.user', 'label': 'Users'},
        {'name': 'auth.group', 'label': 'Groups'},
        {'name': 'accounts.userprofile', 'label': 'User Profiles / Sellers'},
    ]},
    {'label': 'CMS', 'app_label': 'cms', 'items': [
        {'name': 'cms.homeslider', 'label': 'Homepage Sliders'},
        {'name': 'cms.promotioncard', 'label': 'Promotion Cards'},
        {'name': 'cms.banner', 'label': 'Banners'},
        {'name': 'cms.article', 'label': 'Blog Articles'},
        {'name': 'cms.staticpage', 'label': 'Static Pages'},
        {'name': 'cms.aboutpage', 'label': 'About Page'},
        {'name': 'cms.testimonial', 'label': 'Testimonials'},
    ]},
    {'label': 'Reports & Analytics', 'app_label': 'reports', 'items': [
        {'url': '/admin/reports/', 'label': 'Analytics Dashboard'},
        {'name': 'reports.expense', 'label': 'Expense Tracking'},
    ]},
    {'label': 'Settings & Configuration', 'app_label': 'siteconfig', 'items': [
        {'name': 'siteconfig.generalsettings', 'label': 'General Settings'},
        {'name': 'siteconfig.currencytaxsettings', 'label': 'Currency & Tax'},
        {'name': 'siteconfig.paymentgatewaysettings', 'label': 'Payment Gateways'},
        {'name': 'siteconfig.emailsettings', 'label': 'Email Configuration'},
        {'name': 'siteconfig.smssettings', 'label': 'SMS Configuration'},
        {'name': 'siteconfig.websitestylesettings', 'label': 'Website Style Settings'},
        {'name': 'siteconfig.promobannersettings', 'label': 'Promo Banner Settings'},
    ]},
    {'label': 'Notifications', 'app_label': 'notifications', 'items': [
        {'name': 'notifications.notification', 'label': 'Notification Log'},
        {'name': 'notifications.notificationtemplate', 'label': 'Templates'},
        {'name': 'notifications.pushsubscription', 'label': 'Push Subscriptions'},
    ]},
]

JET_SIDE_MENU_CUSTOM_APPS = [
    ('catalog', {'icon': 'fas fa-box'}),
    ('orders', {'icon': 'fas fa-shopping-cart'}),
    ('cart', {'icon': 'fas fa-ticket-alt'}),
    ('reviews', {'icon': 'fas fa-star'}),
    ('wishlist', {'icon': 'fas fa-heart'}),
    ('store', {'icon': 'fas fa-store'}),
    ('auth', {'icon': 'fas fa-users'}),
    ('cms', {'icon': 'fas fa-file-alt'}),
    ('reports', {'icon': 'fas fa-chart-line'}),
    ('siteconfig', {'icon': 'fas fa-cogs'}),
    ('notifications', {'icon': 'fas fa-bell'}),
]
