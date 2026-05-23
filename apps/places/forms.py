"""Search and filter form for the places listing page."""

from django import forms
from .models import Category


class PlaceSearchForm(forms.Form):
    """Stateless search/filter form; no model binding."""

    q = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Search places, locations…",
            "aria-label": "Search places",
        }),
    )
    category = forms.ChoiceField(
        required=False,
        label="Category",
        choices=[("", "All Categories")] + list(Category.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    ordering = forms.ChoiceField(
        required=False,
        label="Sort by",
        choices=[
            ("", "Default"),
            ("rating", "Highest Rated"),
            ("name", "Name A–Z"),
            ("newest", "Newest"),
            ("featured", "Featured First"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
