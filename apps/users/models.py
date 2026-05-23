"""
Custom user model extending AbstractUser.
Keeps the door open for additional profile fields without a separate Profile table.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Extended user model.
    Adds bio and avatar while retaining all built-in Django auth fields.
    """

    email = models.EmailField(_("email address"), unique=True)
    bio = models.TextField(_("bio"), blank=True, max_length=500)
    avatar = models.ImageField(
        _("avatar"),
        upload_to="avatars/",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
        ]

    def __str__(self) -> str:
        return self.username

    @property
    def display_name(self) -> str:
        return self.get_full_name() or self.username

    @property
    def avatar_url(self) -> str:
        if self.avatar:
            return self.avatar.url
        return "/static/images/default-avatar.svg"
