from django.conf import settings


def frontend_settings(request):
    return {
        "api_base_url": settings.API_BASE_URL,
    }