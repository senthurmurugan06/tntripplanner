"""
Places views.
Thin views delegating business logic to services.py.
"""

import json
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView

from .forms import PlaceSearchForm
from .models import TouristPlace, Category
from . import services

logger = logging.getLogger(__name__)


class PlaceListView(ListView):
    """Paginated, searchable, filterable list of tourist places."""

    model = TouristPlace
    template_name = "places/list.html"
    context_object_name = "places"

    def get_queryset(self):
        self.form = PlaceSearchForm(self.request.GET)
        q = self.request.GET.get("q", "").strip()
        category = self.request.GET.get("category", "").strip()
        ordering = self.request.GET.get("ordering", "").strip()
        self.is_unfiltered = not q and not category and not ordering

        qs = services.search_and_filter_places(query=q, category=category, ordering=ordering)

        # Avoid showing featured items twice (featured strip + main grid).
        if self.is_unfiltered:
            self.featured_qs = services.get_featured_places(3)
            qs = qs.exclude(pk__in=self.featured_qs.values_list("pk", flat=True))
        else:
            self.featured_qs = services.get_featured_places(0)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        page = self.request.GET.get("page", 1)
        ctx["page_obj"] = services.paginate_queryset(qs, page)
        ctx["places"] = ctx["page_obj"]  # override the list with paginated result
        ctx["form"] = PlaceSearchForm(self.request.GET)
        ctx["categories"] = Category.choices
        ctx["featured"] = getattr(self, "featured_qs", services.get_featured_places(3))
        ctx["total_count"] = qs.count()
        ctx["current_q"] = self.request.GET.get("q", "")
        ctx["current_category"] = self.request.GET.get("category", "")
        return ctx


class PlaceDetailView(DetailView):
    """Single place detail page."""

    model = TouristPlace
    template_name = "places/detail.html"
    context_object_name = "place"
    slug_field = "slug"

    def get_queryset(self):
        return (
            TouristPlace.objects
            .filter(is_active=True)
            .prefetch_related("favorited_by")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        place = self.object
        ctx["related"] = services.get_related_places(place)
        ctx["is_favorited"] = (
            self.request.user.is_authenticated
            and place.favorited_by.filter(pk=self.request.user.pk).exists()
        )
        return ctx


class ToggleFavoriteView(LoginRequiredMixin, View):
    """AJAX endpoint to toggle a favorite. Returns JSON."""

    def post(self, request, slug):
        place = get_object_or_404(TouristPlace, slug=slug, is_active=True)
        added = services.toggle_favorite(request.user, place)
        return JsonResponse({
            "status": "ok",
            "added": added,
            "favorites_count": place.favorited_by.count(),
        })
