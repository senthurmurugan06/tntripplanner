"""TNTripPlanner URL Configuration."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(pattern_name="places:list", permanent=False), name="home"),
    path("users/", include("apps.users.urls", namespace="users")),
    path("places/", include("apps.places.urls", namespace="places")),
    path("chatbot/", include("apps.chatbot.urls", namespace="chatbot")),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customisation
admin.site.site_header = "TNTripPlanner Admin"
admin.site.site_title = "TNTripPlanner"
admin.site.index_title = "Site Administration"
