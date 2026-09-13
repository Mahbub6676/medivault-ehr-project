from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "first_name", "last_name", "email", "role", "is_active")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("MediVault", {"fields": ("role", "phone")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("MediVault", {"fields": ("role", "phone", "email", "first_name", "last_name")}),
    )


admin.site.site_header = "MediVault EHR Administration"
admin.site.site_title = "MediVault EHR"
admin.site.index_title = "Hospital data management"
