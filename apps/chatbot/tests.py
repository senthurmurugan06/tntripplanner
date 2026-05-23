"""Unit tests for the chatbot app."""

import json
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import ChatMessage
from . import services

User = get_user_model()


class ChatMessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="chatuser", email="chat@test.com", password="SecurePass123!"
        )
        self.msg = ChatMessage.objects.create(
            user=self.user,
            user_message="Tell me about Nashville.",
            ai_response="Nashville is great!",
        )

    def test_str_contains_username(self):
        self.assertIn("chatuser", str(self.msg))

    def test_ordering_by_created_at(self):
        msg2 = ChatMessage.objects.create(
            user=self.user,
            user_message="More?",
            ai_response="Sure!",
        )
        messages = list(ChatMessage.objects.filter(user=self.user))
        self.assertEqual(messages[0], self.msg)
        self.assertEqual(messages[1], msg2)


class CohereServiceTest(TestCase):
    def test_fallback_response_smoky(self):
        svc = services.CohereService()
        resp = svc._fallback_response("Tell me about smoky mountains hiking")
        self.assertIn("TNTripBot", resp)

    def test_fallback_response_nashville(self):
        svc = services.CohereService()
        resp = svc._fallback_response("What to do in Nashville?")
        self.assertIn("TNTripBot", resp)

    def test_fallback_response_generic(self):
        svc = services.CohereService()
        resp = svc._fallback_response("Random question")
        self.assertIn("TNTripBot", resp)

    def test_unconfigured_key_returns_fallback(self):
        svc = services.CohereService()
        svc.api_key = ""
        resp, tokens = svc.get_response("Hello", [])
        self.assertIsInstance(resp, str)
        self.assertEqual(tokens, 0)


class ChatbotViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="viewuser", email="view@test.com", password="SecurePass123!"
        )

    def test_chat_page_requires_login(self):
        response = self.client.get(reverse("chatbot:chat"))
        self.assertEqual(response.status_code, 302)

    def test_chat_page_loads_when_authenticated(self):
        self.client.login(username="viewuser", password="SecurePass123!")
        response = self.client.get(reverse("chatbot:chat"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "chatbot/chat.html")

    def test_send_message_requires_login(self):
        response = self.client.post(
            reverse("chatbot:send"),
            json.dumps({"message": "Hello"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 302)

    def test_send_message_returns_json(self):
        self.client.login(username="viewuser", password="SecurePass123!")
        with patch("apps.chatbot.services._cohere_service.get_response") as mock_resp:
            mock_resp.return_value = ("Great tip!", 50)
            response = self.client.post(
                reverse("chatbot:send"),
                json.dumps({"message": "What's in Nashville?"}),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("ai_response", data)
        self.assertEqual(data["ai_response"], "Great tip!")

    def test_send_empty_message_returns_400(self):
        self.client.login(username="viewuser", password="SecurePass123!")
        response = self.client.post(
            reverse("chatbot:send"),
            json.dumps({"message": ""}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_send_invalid_json_returns_400(self):
        self.client.login(username="viewuser", password="SecurePass123!")
        response = self.client.post(
            reverse("chatbot:send"),
            "not-json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_chat_message_persisted(self):
        self.client.login(username="viewuser", password="SecurePass123!")
        with patch("apps.chatbot.services._cohere_service.get_response") as mock_resp:
            mock_resp.return_value = ("Memphis is amazing!", 30)
            self.client.post(
                reverse("chatbot:send"),
                json.dumps({"message": "Tell me about Memphis"}),
                content_type="application/json",
            )
        self.assertEqual(ChatMessage.objects.filter(user=self.user).count(), 1)
