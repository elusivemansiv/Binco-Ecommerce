from .models import GeneralSettings, CurrencyTaxSettings


def site_settings(request):
    """Inject site settings into every template."""
    general = GeneralSettings.get()
    currency = CurrencyTaxSettings.get()
    return {
        'site_settings': general,
        'currency_settings': currency,
    }
