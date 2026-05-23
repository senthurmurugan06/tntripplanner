"""Admin configuration for the users app."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "date_joined")
    list_filter = ("is_staff", "is_superuser", "is_active", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)

    fieldsets = UserAdmin.fieldsets + (
        (_("Extended Profile"), {"fields": ("bio", "avatar")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (_("Extended Profile"), {"fields": ("email", "bio", "avatar")}),
    )
