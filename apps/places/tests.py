"""Unit tests for the places app."""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import TouristPlace, Category
from . import services

User = get_user_model()


def make_place(**kwargs) -> TouristPlace:
    """Helper factory for TouristPlace objects."""
    defaults = {
        "name": "Test Place",
        "location": "Nashville, TN",
        "category": Category.NATURE,
        "description": "A beautiful test destination.",
        "rating": 4.5,
        "is_active": True,
    }
    defaults.update(kwargs)
    return TouristPlace.objects.create(**defaults)


class TouristPlaceModelTest(TestCase):
    def setUp(self):
        self.place = make_place()

    def test_str_returns_name(self):
        self.assertEqual(str(self.place), "Test Place")

    def test_slug_auto_generated(self):
        self.assertEqual(self.place.slug, "test-place")

    def test_slug_unique_on_duplicate_name(self):
        place2 = make_place(name="Test Place")
        self.assertNotEqual(self.place.slug, place2.slug)
        self.assertIn("test-place", place2.slug)

    def test_get_absolute_url(self):
        url = self.place.get_absolute_url()
        self.assertIn(self.place.slug, url)

    def test_is_free_when_no_fee(self):
        self.assertTrue(self.place.is_free)

    def test_not_free_when_fee_set(self):
        self.place.entry_fee = 10.00
        self.place.save()
        self.assertFalse(self.place.is_free)

    def test_rating_validator(self):
        from django.core.exceptions import ValidationError
        self.place.rating = 6.0
        with self.assertRaises(ValidationError):
            self.place.full_clean()


class PlacesServiceTest(TestCase):
    def setUp(self):
        self.place1 = make_place(name="Smoky Mountains", location="Gatlinburg, TN", category=Category.NATURE)
        self.place2 = make_place(name="Nashville Broadway", location="Nashville, TN", category=Category.ENTERTAINMENT)
        self.place3 = make_place(name="Inactive Place", is_active=False)

    def test_get_active_places_excludes_inactive(self):
        qs = services.get_active_places()
        self.assertNotIn(self.place3, qs)

    def test_search_by_name_case_insensitive(self):
        qs = services.search_and_filter_places(query="smoky")
        self.assertIn(self.place1, qs)

    def test_search_by_location(self):
        qs = services.search_and_filter_places(query="Nashville")
        self.assertIn(self.place2, qs)

    def test_filter_by_category(self):
        qs = services.search_and_filter_places(category=Category.NATURE)
        self.assertIn(self.place1, qs)
        self.assertNotIn(self.place2, qs)

    def test_get_place_by_slug_returns_place(self):
        place = services.get_place_by_slug(self.place1.slug)
        self.assertEqual(place, self.place1)

    def test_get_place_by_slug_returns_none_for_missing(self):
        place = services.get_place_by_slug("does-not-exist")
        self.assertIsNone(place)

    def test_toggle_favorite_add(self):
        user = User.objects.create_user(username="favuser", email="fav@test.com", password="pass")
        added = services.toggle_favorite(user, self.place1)
        self.assertTrue(added)
        self.assertTrue(self.place1.favorited_by.filter(pk=user.pk).exists())

    def test_toggle_favorite_remove(self):
        user = User.objects.create_user(username="favuser2", email="fav2@test.com", password="pass")
        self.place1.favorited_by.add(user)
        added = services.toggle_favorite(user, self.place1)
        self.assertFalse(added)
        self.assertFalse(self.place1.favorited_by.filter(pk=user.pk).exists())


class PlaceListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        for i in range(12):
            make_place(name=f"Place {i}", location="TN")

    def test_list_view_loads(self):
        response = self.client.get(reverse("places:list"))
        self.assertEqual(response.status_code, 200)

    def test_search_filters_results(self):
        make_place(name="Unique Landmark XYZ")
        response = self.client.get(reverse("places:list") + "?q=unique+landmark+xyz")
        self.assertContains(response, "Unique Landmark XYZ")

    def test_pagination(self):
        response = self.client.get(reverse("places:list"))
        self.assertIn("page_obj", response.context)
