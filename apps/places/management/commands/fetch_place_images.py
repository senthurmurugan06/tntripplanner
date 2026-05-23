import mimetypes
import urllib.parse
import time
from pathlib import Path

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import models
from django.utils.text import slugify

from apps.places.models import TouristPlace

HEADERS = {
    "User-Agent": "TNTripPlanner/1.0 (+https://example.com)",
    "Referer": "https://tntripplanner.local",
}


class Command(BaseCommand):
    help = (
        "Download a representative photograph for each tourist place missing an image. "
        "Tries Wikimedia first (no API key needed), then Unsplash's featured endpoint."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without saving any files.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Treat NULL and blank strings as missing.
        qs = TouristPlace.objects.filter(models.Q(image__isnull=True) | models.Q(image=""))

        if not qs.exists():
            self.stdout.write(self.style.SUCCESS("All places already have images."))
            return

        for place in qs:
            base_query = f"{place.name} {place.location}".strip()
            queries = [base_query, place.name]
            if "Waterfalls" in place.name:
                queries.append(place.name.replace("Waterfalls", "Falls"))
            if "Amirthakadeshwarar" in place.name:
                queries.append(place.name.replace("Amirthakadeshwarar", "Amritaghateswarar"))

            self.stdout.write(f'Looking up image for "{place.name}" ({base_query})...')

            image_bytes = None
            extension = ".jpg"
            source = None

            thumb_url = None
            for q in queries:
                thumb_url = self._lookup_wikimedia_thumb(q)
                if thumb_url:
                    break
            if thumb_url:
                try:
                    image_bytes, extension = self._download_image(thumb_url)
                    source = "Wikimedia"
                except Exception as exc:  # noqa: BLE001
                    self.stdout.write(self.style.WARNING(f"  ✗ Wikimedia failed: {exc}"))

            if image_bytes is None:
                unsplash_url = "https://source.unsplash.com/featured/800x600/?" + urllib.parse.quote_plus(base_query)
                image_bytes, source = self._fetch_unsplash(unsplash_url)
                if image_bytes is None:
                    self.stdout.write(self.style.WARNING("  ✗ no Unsplash image available"))
                else:
                    extension = ".jpg"

            if image_bytes is None:
                self.stdout.write(self.style.ERROR("  ✗ no image sources succeeded"))
                continue

            filename = (slugify(place.name) or "place") + extension

            if dry_run:
                self.stdout.write(self.style.NOTICE(f"  would save {filename} from {source}"))
                continue

            place.image.save(filename, ContentFile(image_bytes), save=False)
            if not place.image_alt:
                place.image_alt = place.name
            place.save(update_fields=["image", "image_alt"])
            self.stdout.write(self.style.SUCCESS(f"  ✓ saved {filename} from {source}"))

            # Be a polite client to free APIs.
            time.sleep(0.35)

        self.stdout.write(self.style.SUCCESS("Done."))

    # ── helpers ────────────────────────────────────────────────────────────
    def _lookup_wikimedia_thumb(self, query: str) -> str | None:
        """Return a thumbnail URL from Wikimedia for the query, if available."""
        api_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrlimit": 1,
            "gsrsearch": query,
            "prop": "pageimages",
            "piprop": "thumbnail",
            "pithumbsize": 800,
            "pilicense": "any",
        }

        resp = requests.get(api_url, params=params, timeout=15, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            thumb = page.get("thumbnail", {}).get("source")
            if thumb:
                return thumb
        return None

    def _download_image(self, url: str) -> tuple[bytes, str]:
        """Download image and guess extension."""
        for attempt in range(2):
            resp = requests.get(url, timeout=20, headers=HEADERS)
            if resp.status_code in (429, 503) and attempt == 0:
                time.sleep(1.5)
                continue
            resp.raise_for_status()
            break

        content_type = resp.headers.get("Content-Type", "").split(";")[0].strip()
        ext = mimetypes.guess_extension(content_type) if content_type else None
        if not ext:
            ext = Path(urllib.parse.urlsplit(resp.url).path).suffix
        if not ext or len(ext) > 5:
            ext = ".jpg"

        return resp.content, ext

    def _fetch_unsplash(self, url: str) -> tuple[bytes | None, str | None]:
        """Hit Unsplash featured endpoint with a small retry."""
        last_exc: Exception | None = None
        for attempt in range(2):
            try:
                resp = requests.get(url, timeout=20, headers=HEADERS)
                if resp.status_code in (429, 503) and attempt == 0:
                    time.sleep(1.5)
                    continue
                resp.raise_for_status()
                return resp.content, "Unsplash"
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
        self.stdout.write(self.style.WARNING(f"  ✗ Unsplash failed: {last_exc}"))
        return None, None
