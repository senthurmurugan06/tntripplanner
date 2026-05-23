"""
Chatbot service layer.
All Cohere API communication is encapsulated here.
Views never import cohere directly.
"""

import json
import logging
import re
import time
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model

from apps.places.models import TouristPlace
from .models import ChatMessage

logger = logging.getLogger(__name__)

User = get_user_model()

# System prompt that shapes the AI's persona and knowledge scope
SYSTEM_PROMPT = """You are TNTripBot, an expert travel assistant specializing in
Tamil Nadu tourism. You help visitors discover amazing places, plan itineraries,
understand local culture, and get travel tips.

Formatting rules (always apply):
- Respond ONLY in concise bullet points. Do not return long paragraphs.
- Do not write any introductory paragraph. Start every answer with a bullet.
- Start each bullet with "- " and keep one idea per line.
- For any travel or place query, include bold section labels inside bullets: **How to reach**, **Best time to visit**, **Entry fees**, **Nearby attractions**, **Accommodation**.
- If the user asks any question, break the answer into bullets even if a paragraph would seem easier.

Key Knowledge Base:
- **Madurai**: Ancient city called 'Thoonga Nagaram' (city that never sleeps). Home to Meenakshi Amman Temple, Gandhi Memorial Museum, Thirumohoor Kalamegaperumal Temple, Koodal Azhagar Temple, Aayiram Kaal Mandapam, Samanar Hills. Referred to as 'Athens of the East'. Weather: Tropical, best time November-February. Reach by NH 45/49, buses from M.G.R. Bus Stand, airport with international flights, railway from Madurai Junction. Accommodation: Hotel Tamilnadu options. Nearby: Kazimar Periya Pallivasal, Thirumalai Nayakar Mahal.
- **Chennai**: Capital city, formerly Madras. Cultural capital of South India. Beaches, temples, museums. Top attractions: Guindy Nature Park, Crocodile Park, Kapaleeshwarar Temple, Sri Parthasarathy Temple, Sri Ramakrishna Math. Weather: Tropical, best time December-February. Reach by CMBT/MMBT bus terminals, Chennai International Airport, railway stations (Central, Egmore, Beach), Metro. Accommodation: Various hotels. Nearby: Thousand Lights Mosque, Government Museum.
- **Ooty**: Queen of Hill Stations, 'Switzerland of India'. Top attractions: Government Botanical Garden, Ooty Lake, Pine Forest, Deer Park, Avalanche Lake, Doddabetta. Things to do: Toy Train ride, trekking, boating. Weather: Cool year-round, best time March-May and September-November. Reach by Udhagamandalam Central Bus Stand, Coimbatore Airport (88km), Coimbatore Railway Station (87km), Toy Train from Mettupalayam. Accommodation: Hotel Tamilnadu - Ooty I, Youth Hostel. Nearby: Lake Park, Lake Boat House.
- **Rameswaram**: Holy pilgrimage site, one of Char Dham. Home to Ramanathaswamy Temple (12 jyotirlinga), Dhanushkodi Beach, Dr. A P J Abdul Kalam Memorial, Pamban Bridge, Ram Sethu, Villoondi Theertham. Closest point to Sri Lanka. Weather: Tropical, best time October-March. Reach by buses from Chennai/Madurai, Madurai Airport (180km), Rameswaram Railway Station. Accommodation: Hotel Tamilnadu - Rameswaram. Nearby: Agni Theertham Beach, Sangumal Beach.

Guidelines:
- Focus on Tamil Nadu destinations, attractions, culture, food, and travel logistics.
- Be friendly, enthusiastic, and knowledgeable.
- Provide specific, actionable advice rather than generic tips.
- If asked about places outside Tamil Nadu, briefly acknowledge but redirect to TN (Tamil Nadu).
- For detailed queries about specific places (how to reach, best time to visit, entry fees, nearby attractions, accommodation), provide comprehensive information using bullet points for clarity.
- Structure responses with bullet points when listing multiple options, steps, or details.
- When providing information about places, include sections for:
  - How to reach
  - Best time to visit
  - Entry fees
  - Nearby attractions
  - Accommodation options
- Use emojis sparingly to add warmth.
"""


class ChatbotError(Exception):
    """Raised when the chatbot service encounters an unrecoverable error."""


class CohereService:
    """
    Wraps Cohere HTTP calls.
    Handles timeout, retries, error mapping, and graceful fallback.
    """

    def __init__(self):
        self.api_key: str = settings.COHERE_API_KEY
        self.model: str = settings.COHERE_MODEL
        self.max_tokens: int = settings.COHERE_MAX_TOKENS
        self.timeout: int = settings.COHERE_TIMEOUT

    def _is_configured(self) -> bool:
        return bool(self.api_key and self.api_key != "")

    def get_response(
        self,
        user_message: str,
        conversation_history: list[dict],
    ) -> tuple[str, int]:
        """
        Send a message to Cohere and return (response_text, tokens_used).
        Falls back gracefully if the API is unavailable or unconfigured.
        """
        if not self._is_configured():
            logger.warning("Cohere API key not configured; using fallback response.")
            return self._fallback_response(user_message), 0

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(conversation_history[-10:])  # Keep last 10 turns for context
        messages.append({"role": "user", "content": user_message})

        try:
            return self._call_cohere(messages)
        except ChatbotError as e:
            error_msg = str(e).lower()
            if "quota exceeded" in error_msg:
                return self._quota_exceeded_response(user_message), 0
            elif "invalid api key" in error_msg:
                return self._invalid_key_response(user_message), 0
            else:
                return self._fallback_response(user_message), 0
        except Exception as exc:
            logger.error("Cohere API error: %s", exc, exc_info=True)
            return self._fallback_response(user_message), 0

    def _call_cohere(self, messages: list[dict]) -> tuple[str, int]:
        """Make the actual HTTP request to Cohere."""
        import cohere

        client = cohere.Client(self.api_key)

        # Extract the user message (last message)
        user_message = messages[-1]["content"]

        # Build conversation history for Cohere (chat_history)
        chat_history = []
        for msg in messages[1:-1]:  # Skip system prompt and current message
            if msg["role"] == "user":
                chat_history.append({
                    "role": "user",
                    "content": msg["content"]
                })
            elif msg["role"] == "assistant":
                chat_history.append({
                    "role": "assistant",
                    "content": msg["content"]
                })

        def _send_chat(model_name: str):
            return client.chat(
                model=model_name,
                message=user_message,
                max_tokens=self.max_tokens,
                temperature=0.7,
            )

        # If configured model has been deprecated/removed, try available valid chat models.
        fallback_models = [
            "command-r-08-2024",
            "command-a-reasoning-08-2025",
            "tiny-aya-water",
            "command-a-vision-07-2025"
        ]

        try:
            last_exc = None
            model_to_try = [self.model] + [m for m in fallback_models if m != self.model]

            for model_name in model_to_try:
                try:
                    response = _send_chat(model_name)
                    self.model = model_name
                    break
                except Exception as e:
                    last_exc = e
                    err_text = str(e).lower()
                    if "not found" in err_text or "removed" in err_text or "model" in err_text:
                        continue  # try next fallback model
                    raise
            else:
                raise ChatbotError(f"Cohere API model error: {last_exc}") from last_exc

            # Parse response content with robust handling
            if hasattr(response, "text") and isinstance(response.text, str):
                text = response.text
            elif hasattr(response, "message"):
                msg = response.message
                if isinstance(msg, dict):
                    text = msg.get("content", "")
                elif hasattr(msg, "content"):
                    text = msg.content
                else:
                    text = str(msg)
            elif hasattr(response, "chat_history") and response.chat_history:
                # fall back to latest chatbot message in history
                last_msg = response.chat_history[-1]
                text = getattr(last_msg, "message", str(last_msg))
            else:
                text = str(response)

            text = text.strip() if isinstance(text, str) else str(text)
            text = self._normalize_bullet_response(text)

            # Attempt to parse tokens from response metadata if available
            tokens = 0
            if hasattr(response, "meta") and getattr(response.meta, "tokens", None):
                tokens_meta = response.meta.tokens
                if hasattr(tokens_meta, "output_tokens") and tokens_meta.output_tokens is not None:
                    tokens = int(tokens_meta.output_tokens)
                elif hasattr(tokens_meta, "tokens") and tokens_meta.tokens is not None:
                    tokens = int(tokens_meta.tokens)

            return text, tokens
        except Exception as e:
            error_msg = str(e).lower()
            if "unauthorized" in error_msg or "invalid" in error_msg or "invalid api key" in error_msg:
                raise ChatbotError("Invalid API key. Please contact the administrator to update the Cohere API key.") from e
            elif "rate" in error_msg or "quota" in error_msg or "429" in error_msg:
                raise ChatbotError("API quota exceeded. Please try again later or contact the administrator.") from e
            else:
                raise ChatbotError(f"Cohere API error: {str(e)}") from e

    def _normalize_bullet_response(self, text: str) -> str:
        """Convert responses into bullet points when needed."""
        if not isinstance(text, str) or not text.strip():
            return text

        lines = text.splitlines()
        normalized_lines = []
        prev_is_list = False

        for line in lines:
            raw = line.rstrip()
            stripped = raw.strip()
            if not stripped:
                normalized_lines.append("")
                prev_is_list = False
                continue

            if stripped.startswith(('-', '*', '•')) or re.match(r'^[0-9]+[\.)]\s+', stripped):
                normalized_lines.append(stripped)
                prev_is_list = True
            elif prev_is_list and raw.startswith(" "):
                normalized_lines.append(raw)
            else:
                normalized_lines.append(f"- {stripped}")
                prev_is_list = True

        return "\n".join(normalized_lines)

    @staticmethod
    def _fallback_response(user_message: str) -> str:
        """
        Return a contextual fallback when the API is unavailable.
        Prevents the UI from showing a blank or error response.
        """
        message_lower = user_message.lower()
        if any(w in message_lower for w in ["beach", "chennai", "marina", "elliot"]):
            return (
                "- Chennai beaches: Marina for sunrise walks; Elliot's for calmer evenings\n"
                "- Pair with: Kapaleeshwarar Temple (Mylapore) + filter coffee on RK Salai\n"
                "- Note: Fallback mode; ask again later for deeper tips"
            )
        if any(w in message_lower for w in ["temple", "madurai", "srirangam", "rameswaram"]):
            return (
                "- Temple circuit: Meenakshi Amman (Madurai), Sri Ranganathaswamy (Srirangam), Ramanathaswamy (Rameswaram)\n"
                "- Tip: Visit at dawn for cooler weather and shorter queues\n"
                "- Note: Fallback mode; ask again later for more details"
            )
        if any(w in message_lower for w in ["ooty", "kodaikanal", "hill", "ghats"]):
            return (
                "- Ooty: Botanical Garden, Nilgiri Mountain Railway\n"
                "- Kodaikanal: Coaker's Walk, Pillar Rocks, lake boating\n"
                "- Note: Fallback mode; ask again later for trek routes and timings"
            )
        return (
            "- Welcome to TNTripBot (fallback mode)\n"
            "- Ask about: Chennai beaches, Madurai/Srirangam temples, Ooty/Kodaikanal hills, or specific activities\n"
            "- Full AI assistance needs a valid Cohere API key; contact the admin"
        )

    @staticmethod
    def _quota_exceeded_response(user_message: str) -> str:
        """
        Return a specific message when API quota is exceeded.
        """
        return (
            "I'm sorry, the chatbot has reached its API usage limit for today. 🌟 "
            "I'm still here to help with basic information about Tamil Nadu! "
            "Try asking about Chennai beaches, Madurai temples, Ooty/Kodaikanal hills, "
            "or general travel tips. The full AI assistance will be back tomorrow!"
        )

    @staticmethod
    def _invalid_key_response(user_message: str) -> str:
        """
        Return a specific message when API key is invalid.
        """
        return (
            "I'm sorry, the chatbot service is not configured correctly. Please contact the administrator to set a valid COHERE_API_KEY."
        )


# Module-level singleton to avoid recreating the client per request
_cohere_service = CohereService()


def get_conversation_history(user) -> list[dict]:
    """Load recent conversation history for the Cohere context window."""
    messages = (
        ChatMessage.objects
        .filter(user=user)
        .order_by("-created_at")[:10]
        .values("user_message", "ai_response")
    )
    history = []
    for msg in reversed(list(messages)):
        history.append({"role": "user", "content": msg["user_message"]})
        history.append({"role": "assistant", "content": msg["ai_response"]})
    return history


def find_related_place(ai_response: str) -> Optional[TouristPlace]:
    """
    Attempt to link the AI response to a known tourist place.
    Simple heuristic: check if any place name appears in the response.
    """
    places = TouristPlace.objects.filter(is_active=True).only("id", "name")
    response_lower = ai_response.lower()
    for place in places:
        if place.name.lower() in response_lower:
            return place
    return None


def process_chat_message(user, user_message: str) -> ChatMessage:
    """
    Orchestrate a full chat exchange:
    1. Build conversation history
    2. Call Cohere
    3. Find related place (optional)
    4. Persist and return the ChatMessage
    """
    history = get_conversation_history(user)
    ai_response, tokens = _cohere_service.get_response(user_message, history)
    related_place = find_related_place(ai_response)

    chat = ChatMessage.objects.create(
        user=user,
        user_message=user_message,
        ai_response=ai_response,
        related_place=related_place,
        tokens_used=tokens,
    )
    return chat
