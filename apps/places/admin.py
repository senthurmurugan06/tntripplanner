"""Admin config for tourist places."""

from django.contrib import admin
from django.utils.html import format_html

from .models import TouristPlace


@admin.register(TouristPlace)
class TouristPlaceAdmin(admin.ModelAdmin):
    list_display = (
        "name", "location", "category", "rating",
        "is_featured", "is_active", "favorites_count", "created_at",
    )
    list_filter = ("category", "is_featured", "is_active", "state")
    search_fields = ("name", "location", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at", "favorites_count", "image_preview")
    ordering = ("-created_at",)
    list_per_page = 25

    fieldsets = (
        ("Core", {"fields": ("name", "slug", "location", "state", "category")}),
        ("Content", {"fields": ("description", "short_description", "image", "image_alt", "image_preview")}),
        ("Details", {"fields": ("rating", "rating_count", "entry_fee", "address", "latitude", "longitude")}),
        ("Contact", {"fields": ("website", "phone")}),
        ("Flags", {"fields": ("is_featured", "is_active")}),
        ("Meta", {"fields": ("created_at", "updated_at", "favorites_count")}),
    )

    filter_horizontal = ("favorited_by",)

    @admin.display(description="Favorites")
    def favorites_count(self, obj):
        return obj.favorited_by.count()

    @admin.display(description="Image Preview")
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="120" />', obj.image.url)
        return "No image"
