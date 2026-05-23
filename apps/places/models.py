"""
Tourist place models.
Indexed fields, category choices, validated rating, M2M favorites.
"""

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Category(models.TextChoices):
    NATURE = "nature", _("Nature & Parks")
    HISTORY = "history", _("Historical Sites")
    CULTURE = "culture", _("Culture & Arts")
    ADVENTURE = "adventure", _("Adventure & Sports")
    FOOD = "food", _("Food & Cuisine")
    ENTERTAINMENT = "entertainment", _("Entertainment")
    RELIGIOUS = "religious", _("Religious Sites")
    SHOPPING = "shopping", _("Shopping")
    OTHER = "other", _("Other")


class TouristPlace(models.Model):
    """
    Core model representing a tourist destination.
    Uses db_index on searchable fields; slug for SEO-friendly URLs.
    """

    name = models.CharField(_("name"), max_length=200, db_index=True)
    slug = models.SlugField(_("slug"), max_length=220, unique=True, blank=True)
    location = models.CharField(_("location"), max_length=300, db_index=True)
    state = models.CharField(_("state"), max_length=100, default="Tamil Nadu", db_index=True)
    category = models.CharField(
        _("category"),
        max_length=30,
        choices=Category.choices,
        default=Category.OTHER,
        db_index=True,
    )
    description = models.TextField(_("description"))
    short_description = models.CharField(_("short description"), max_length=300, blank=True)

    # Validated rating: 1.0 – 5.0
    rating = models.DecimalField(
        _("rating"),
        max_digits=3,
        decimal_places=1,
        default=3.0,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
    )
    rating_count = models.PositiveIntegerField(_("rating count"), default=0)

    # Media
    image = models.ImageField(
        _("image"),
        upload_to="places/%Y/%m/",
        null=True,
        blank=True,
    )
    image_alt = models.CharField(_("image alt text"), max_length=200, blank=True)

    # Address details
    address = models.CharField(_("address"), max_length=400, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Contact
    website = models.URLField(_("website"), blank=True)
    phone = models.CharField(_("phone"), max_length=20, blank=True)

    # Admission
    entry_fee = models.DecimalField(
        _("entry fee ($)"),
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Leave blank if free."),
    )

    # M2M — users who favorited this place
    favorited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="favorite_places",
        blank=True,
        verbose_name=_("favorited by"),
    )

    # Lifecycle
    is_featured = models.BooleanField(_("featured"), default=False, db_index=True)
    is_active = models.BooleanField(_("active"), default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("tourist place")
        verbose_name_plural = _("tourist places")
        ordering = ["-is_featured", "-rating", "name"]
        indexes = [
            models.Index(fields=["name", "location"]),
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["is_featured", "rating"]),
        ]
        constraints = [
            UniqueConstraint(Lower("name"), name="uniq_place_name_ci"),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while TouristPlace.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("places:detail", kwargs={"slug": self.slug})

    @property
    def image_url(self) -> str:
        """Return the URL to display for this place's image.

        - If an image file has been uploaded, use its URL.
        - Otherwise fall back to a generic placeholder stored in static files.
          and, for a bit more visual interest, hit Unsplash with the place
          name as a keyword.  That way you’ll usually see a relevant photo
          even before anything has been saved to the database (e.g. for
          "Brihadeeswarar Temple").
        """
        if self.image:
            return self.image.url

        # unsplash offers a very simple public endpoint that returns a random
        # image matching the query terms. we append the place name so searches
        # like "Brihadeeswarar Temple" will return something reasonably
        # appropriate without requiring an API key. the dimensions are modest
        # to keep pages small.
        try:
            from urllib.parse import quote_plus
            query = quote_plus(self.name)
            return f"https://source.unsplash.com/featured/600x400/?{query}"
        except Exception:
            # if anything goes wrong, fall back to our generic placeholder image
            return "/static/images/placeholder.svg"

    @property
    def is_free(self) -> bool:
        return self.entry_fee is None or self.entry_fee == 0

    @property
    def star_range(self):
        """Returns range for template star rendering."""
        return range(1, 6)
