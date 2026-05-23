"""URL patterns for the places app."""

from django.urls import path
from . import views

app_name = "places"

urlpatterns = [
    path("", views.PlaceListView.as_view(), name="list"),
    path("<slug:slug>/", views.PlaceDetailView.as_view(), name="detail"),
    path("<slug:slug>/favorite/", views.ToggleFavoriteView.as_view(), name="toggle-favorite"),
]
