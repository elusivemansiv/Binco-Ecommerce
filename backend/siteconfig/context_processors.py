from .models import GeneralSettings, CurrencyTaxSettings, WebsiteStyleSettings, PromoBannerSettings


def site_settings(request):
    """Inject site settings into every template."""
    general = GeneralSettings.get()
    currency = CurrencyTaxSettings.get()
    styles = WebsiteStyleSettings.get()
    promo = PromoBannerSettings.get()
    return {
        'site_settings': general,
        'currency_settings': currency,
        'style_settings': styles,
        'promo_banner': promo,
    }
