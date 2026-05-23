"""
Business-logic service for the users app.
Views remain thin; all complex logic lives here.
"""

import logging
from typing import Optional

from django.contrib.auth import update_session_auth_hash
from django.http import HttpRequest

from .models import CustomUser

logger = logging.getLogger(__name__)


def update_user_profile(
    user: CustomUser,
    request: HttpRequest,
    form_data: dict,
    files: Optional[dict] = None,
) -> CustomUser:
    """
    Persist profile changes.
    Keeps the user logged-in after email/password change.
    """
    for field, value in form_data.items():
        setattr(user, field, value)

    if files and "avatar" in files:
        user.avatar = files["avatar"]

    user.save()
    logger.info("Profile updated for user %s", user.username)
    return user


def get_user_favorites_count(user: CustomUser) -> int:
    """Return the number of places a user has favorited."""
    return user.favorite_places.count()
