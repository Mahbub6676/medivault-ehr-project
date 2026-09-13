from django.urls import path

from . import views

app_name = "appointments"

urlpatterns = [
    path("", views.appointment_list, name="list"),
    path("add/", views.appointment_add, name="add"),
    path("request/", views.patient_appointment_request, name="request"),
    path("<int:pk>/", views.appointment_detail, name="detail"),
    path("<int:pk>/edit/", views.appointment_edit, name="edit"),
    path("<int:pk>/status/<str:status>/", views.appointment_set_status, name="set_status"),
]

