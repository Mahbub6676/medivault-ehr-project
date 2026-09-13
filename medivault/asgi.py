"""ASGI config for the MediVault EHR project."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medivault.settings")

application = get_asgi_application()
