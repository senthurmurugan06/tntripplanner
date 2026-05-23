"""
Chatbot models.
Stores every user/AI message pair with optional tourist place reference.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ChatMessage(models.Model):
    """
    Stores a single user→AI exchange.
    Indexed on user + timestamp for efficient history retrieval.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chatmessage_set",
        verbose_name=_("user"),
    )
    user_message = models.TextField(_("user message"))
    ai_response = models.TextField(_("AI response"))

    # Optional: link this exchange to a relevant tourist place
    related_place = models.ForeignKey(
        "places.TouristPlace",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chat_references",
        verbose_name=_("related place"),
    )

    # Token tracking for monitoring / cost awareness
    tokens_used = models.PositiveIntegerField(_("tokens used"), default=0)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _("chat message")
        verbose_name_plural = _("chat messages")
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.username} @ {self.created_at:%Y-%m-%d %H:%M}: {self.user_message[:50]}"
