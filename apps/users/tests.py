"""Unit tests for the users app."""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserModelTest(TestCase):
    """Tests for the CustomUser model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            first_name="Jane",
            last_name="Doe",
        )

    def test_str_returns_username(self):
        self.assertEqual(str(self.user), "testuser")

    def test_display_name_full_name(self):
        self.assertEqual(self.user.display_name, "Jane Doe")

    def test_display_name_falls_back_to_username(self):
        self.user.first_name = ""
        self.user.last_name = ""
        self.assertEqual(self.user.display_name, "testuser")

    def test_email_is_unique(self):
        with self.assertRaises(Exception):
            User.objects.create_user(
                username="another",
                email="test@example.com",
                password="SecurePass123!",
            )

    def test_avatar_url_default(self):
        self.assertIn("default-avatar", self.user.avatar_url)


class RegistrationViewTest(TestCase):
    """Tests for the registration flow."""

    def setUp(self):
        self.client = Client()
        self.url = reverse("users:register")

    def test_register_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")

    def test_successful_registration(self):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_duplicate_email_rejected(self):
        User.objects.create_user(username="existing", email="taken@example.com", password="pass")
        data = {
            "username": "newuser2",
            "email": "taken@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "email", "An account with this email already exists.")


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="loginuser", email="login@example.com", password="SecurePass123!")
        self.url = reverse("users:login")

    def test_login_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_valid_login_redirects(self):
        response = self.client.post(self.url, {"username": "loginuser", "password": "SecurePass123!"})
        self.assertEqual(response.status_code, 302)

    def test_invalid_login_stays(self):
        response = self.client.post(self.url, {"username": "loginuser", "password": "wrong"})
        self.assertEqual(response.status_code, 200)


class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="profileuser", email="profile@example.com", password="SecurePass123!")

    def test_profile_requires_login(self):
        response = self.client.get(reverse("users:profile"))
        self.assertRedirects(response, "/users/login/?next=/users/profile/")

    def test_profile_accessible_when_logged_in(self):
        self.client.login(username="profileuser", password="SecurePass123!")
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)
