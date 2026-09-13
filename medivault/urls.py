"""Root URL configuration for MediVault EHR."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.views.generic import TemplateView


def health(request):
    """Simple health-check endpoint used by the hosting sandbox."""
    return JsonResponse({"status": "ok", "app": "MediVault EHR"})


urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("patients/", include("patients.urls")),
    path("doctors/", include("doctors.urls")),
    path("appointments/", include("appointments.urls")),
    path("medical-records/", include("medical_records.urls")),
    path("prescriptions/", include("prescriptions.urls")),
    path("lab-tests/", include("lab_tests.urls")),
    path("billing/", include("billing.urls")),
    path("notifications/", include("notifications.urls")),
    # Health check (both with and without trailing slash)
    path("api/health", health, name="health"),
    path("api/health/", health, name="health-slash"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler403 = "accounts.views.error_403"
handler404 = "accounts.views.error_404"
handler500 = "accounts.views.error_500"
