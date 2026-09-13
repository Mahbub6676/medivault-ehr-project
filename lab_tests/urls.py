from django.urls import path

from . import views

app_name = "lab_tests"

urlpatterns = [
    path("", views.lab_test_list, name="list"),
    path("add/", views.lab_test_add, name="add"),
    path("<int:pk>/", views.lab_test_detail, name="detail"),
    path("<int:pk>/edit/", views.lab_test_edit, name="edit"),
]
