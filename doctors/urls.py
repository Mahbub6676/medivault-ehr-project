from django.urls import path

from . import views

app_name = "doctors"

urlpatterns = [
    path("", views.doctor_list, name="doctor_list"),
    path("add/", views.doctor_add, name="doctor_add"),
    path("<int:pk>/", views.doctor_detail, name="doctor_detail"),
    path("<int:pk>/edit/", views.doctor_edit, name="doctor_edit"),
    path("<int:pk>/toggle/", views.doctor_toggle_active, name="doctor_toggle"),
    path("departments/", views.department_list, name="department_list"),
    path("departments/add/", views.department_add, name="department_add"),
    path("departments/<int:pk>/edit/", views.department_edit, name="department_edit"),
]
