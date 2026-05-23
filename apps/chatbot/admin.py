"""Admin for the chatbot app."""

from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("user", "short_message", "short_response", "related_place", "tokens_used", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "user_message", "ai_response")
    readonly_fields = ("user", "user_message", "ai_response", "related_place", "tokens_used", "created_at")
    ordering = ("-created_at",)
    list_per_page = 50

    @admin.display(description="User Message")
    def short_message(self, obj):
        return obj.user_message[:60] + ("…" if len(obj.user_message) > 60 else "")

    @admin.display(description="AI Response")
    def short_response(self, obj):
        return obj.ai_response[:60] + ("…" if len(obj.ai_response) > 60 else "")
