"""
Chatbot views.
- GET  /chatbot/      → render the chat UI with history
- POST /chatbot/send/ → JSON endpoint for async message exchange
- GET  /chatbot/history/ → paginated history (optional)
"""

import json
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView

from .models import ChatMessage
from . import services
from apps.places.models import TouristPlace

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 1000  # chars


class ChatbotView(LoginRequiredMixin, TemplateView):
    """Renders the chatbot UI with the last N messages for history display."""

    template_name = "chatbot/chat.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["chat_history"] = (
            ChatMessage.objects
            .filter(user=self.request.user)
            .select_related("related_place")
            .order_by("-created_at")[:20]
        )
        ctx["places"] = TouristPlace.objects.filter(is_active=True).order_by("name")
        return ctx


class SendMessageView(LoginRequiredMixin, View):
    """
    POST endpoint — accepts JSON, returns JSON.
    CSRF protected via Django middleware (cookie + header).
    """

    def post(self, request):
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "Invalid JSON payload."}, status=400)

        user_message = body.get("message", "").strip()

        if not user_message:
            return JsonResponse({"error": "Message cannot be empty."}, status=400)

        if len(user_message) > MAX_MESSAGE_LENGTH:
            return JsonResponse(
                {"error": f"Message too long. Maximum {MAX_MESSAGE_LENGTH} characters."},
                status=400,
            )

        try:
            chat = services.process_chat_message(request.user, user_message)
        except Exception as exc:
            logger.error("Chatbot processing error for user %s: %s", request.user.username, exc, exc_info=True)
            return JsonResponse(
                {"error": "An unexpected error occurred. Please try again."},
                status=500,
            )

        response_data = {
            "id": chat.pk,
            "user_message": chat.user_message,
            "ai_response": chat.ai_response,
            "created_at": chat.created_at.isoformat(),
        }

        if chat.related_place:
            response_data["related_place"] = {
                "name": chat.related_place.name,
                "url": chat.related_place.get_absolute_url(),
                "slug": chat.related_place.slug,
            }

        return JsonResponse(response_data, status=200)


class ClearHistoryView(LoginRequiredMixin, View):
    """DELETE all chat messages for the current user."""

    def post(self, request):
        deleted_count, _ = ChatMessage.objects.filter(user=request.user).delete()
        return JsonResponse({"deleted": deleted_count})
