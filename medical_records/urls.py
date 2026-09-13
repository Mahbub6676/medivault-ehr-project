from django.urls import path

from . import views

app_name = "medical_records"

urlpatterns = [
    path("", views.record_list, name="list"),
    path("add/", views.record_add, name="add"),
    path("<int:pk>/", views.record_detail, name="detail"),
    path("<int:pk>/edit/", views.record_edit, name="edit"),
    path("<int:pk>/print/", views.record_print, name="print"),
]
