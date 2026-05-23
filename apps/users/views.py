"""User views: register, login, logout, profile."""

import logging

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView

from .forms import RegistrationForm, CustomLoginForm, ProfileUpdateForm
from .models import CustomUser

logger = logging.getLogger(__name__)


class RegisterView(CreateView):
    """User registration view."""

    model = CustomUser
    form_class = RegistrationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("places:list")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("places:list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f"Welcome to TNTripPlanner, {user.username}! 🎉")
        logger.info("New user registered: %s", user.username)
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class CustomLoginView(LoginView):
    """Custom login view."""

    form_class = CustomLoginForm
    template_name = "users/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().username}!")
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    """Logout then redirect to login page."""
    next_page = reverse_lazy("users:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "You have been logged out.")
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, DetailView):
    """Display the current user's profile."""

    model = CustomUser
    template_name = "users/profile.html"
    context_object_name = "profile_user"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["favorites"] = user.favorite_places.select_related().order_by("-name")[:6]
        ctx["favorites_count"] = user.favorite_places.count()
        ctx["chat_count"] = user.chatmessage_set.count()
        return ctx


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Edit the current user's profile."""

    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)
