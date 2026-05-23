"""URL patterns for the chatbot app."""

from django.urls import path
from . import views

app_name = "chatbot"

urlpatterns = [
    path("", views.ChatbotView.as_view(), name="chat"),
    path("send/", views.SendMessageView.as_view(), name="send"),
    path("clear/", views.ClearHistoryView.as_view(), name="clear"),
]
