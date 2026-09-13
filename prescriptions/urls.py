from django.urls import path

from . import views

app_name = "prescriptions"

urlpatterns = [
    path("", views.prescription_list, name="list"),
    path("add/", views.prescription_add, name="add"),
    path("<int:pk>/", views.prescription_detail, name="detail"),
    path("<int:pk>/edit/", views.prescription_edit, name="edit"),
    path("<int:pk>/print/", views.prescription_print, name="print"),
]
