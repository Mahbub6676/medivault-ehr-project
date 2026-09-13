"""WSGI config for the MediVault EHR project."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medivault.settings")

application = get_wsgi_application()
