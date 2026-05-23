"""
Places service layer.
All query logic lives here; views stay thin.
Optimises N+1 issues with select_related / prefetch_related.
"""

import logging
from typing import Optional

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, QuerySet

from .models import TouristPlace, Category

logger = logging.getLogger(__name__)

PER_PAGE = getattr(settings, "PLACES_PER_PAGE", 9)


def get_active_places() -> QuerySet:
    """Base queryset: active places only, optimised."""
    return (
        TouristPlace.objects
        .filter(is_active=True)
        .prefetch_related("favorited_by")
    )


def search_and_filter_places(
    query: str = "",
    category: str = "",
    ordering: str = "",
) -> QuerySet:
    """
    Case-insensitive search across name, location, description.
    Optionally filter by category and sort by ordering param.
    """
    qs = get_active_places()

    if query:
        qs = qs.filter(
            Q(name__icontains=query)
            | Q(location__icontains=query)
            | Q(description__icontains=query)
            | Q(short_description__icontains=query)
        )

    if category and category in Category.values:
        qs = qs.filter(category=category)

    ordering_map = {
        "rating": "-rating",
        "name": "name",
        "newest": "-created_at",
        "featured": "-is_featured",
    }
    if ordering in ordering_map:
        qs = qs.order_by(ordering_map[ordering])

    return qs


def paginate_queryset(qs: QuerySet, page: int, per_page: int = PER_PAGE):
    """Return a page object from a queryset."""
    paginator = Paginator(qs, per_page)
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


def get_place_by_slug(slug: str) -> Optional[TouristPlace]:
    """Fetch a single active place by slug; returns None if not found."""
    try:
        return (
            TouristPlace.objects
            .filter(is_active=True)
            .prefetch_related("favorited_by")
            .get(slug=slug)
        )
    except TouristPlace.DoesNotExist:
        logger.warning("Place not found: %s", slug)
        return None


def get_featured_places(limit: int = 3) -> QuerySet:
    """Return featured places for the home/sidebar widget."""
    return get_active_places().filter(is_featured=True)[:limit]


def get_related_places(place: TouristPlace, limit: int = 3) -> QuerySet:
    """Return same-category places, excluding self."""
    return (
        get_active_places()
        .filter(category=place.category)
        .exclude(pk=place.pk)[:limit]
    )


def toggle_favorite(user, place: TouristPlace) -> bool:
    """
    Toggle a user's favorite status for a place.
    Returns True if added, False if removed.
    """
    if place.favorited_by.filter(pk=user.pk).exists():
        place.favorited_by.remove(user)
        logger.debug("User %s removed favorite: %s", user.username, place.name)
        return False
    place.favorited_by.add(user)
    logger.debug("User %s added favorite: %s", user.username, place.name)
    return True
