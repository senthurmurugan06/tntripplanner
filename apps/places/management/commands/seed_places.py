"""
Management command: seed_places
Usage: python manage.py seed_places

Populates the database with sample Tamil Nadu tourist places for development.
"""

from django.core.management.base import BaseCommand
from apps.places.models import TouristPlace, Category


SAMPLE_PLACES = [
    {
        "name": "Brihadeeswarar Temple",
        "location": "Thanjavur, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": Category.RELIGIOUS,
        "description": (
            "UNESCO-listed Chola temple built by Raja Raja I with a soaring 66m vimana, granite sculptures, "
            "and frescoes. An architectural masterpiece of the 11th century."
        ),
        "short_description": "Iconic 11th-century Chola Shiva temple with towering vimana.",
        "rating": 4.9,
        "rating_count": 42000,
        "entry_fee": None,
        "is_featured": True,
        "address": "Membalam Rd, Balaganapathy Nagar, Thanjavur, Tamil Nadu",
    },
    {
        "name": "Meenakshi Amman Temple",
        "location": "Madurai, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": Category.RELIGIOUS,
        "description": (
            "Vibrant Dravidian temple complex with 14 gopurams, thousands of colorful sculptures, and "
            "the famed Hall of Thousand Pillars. A living center of worship on the Vaigai river."
        ),
        "short_description": "Grand Dravidian temple famed for towering gopurams and sculpture.",
        "rating": 4.8,
        "rating_count": 51000,
        "entry_fee": None,
        "is_featured": True,
        "address": "Madurai Main, Madurai, Tamil Nadu",
    },
    {
        "name": "Marina Beach",
        "location": "Chennai, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": Category.NATURE,
        "description": (
            "One of the world's longest urban beaches, popular for sunrise walks, kolam sands, and "
            "evening street food. Landmarks nearby include the Lighthouse and heritage buildings on Kamarajar Salai."
        ),
        "short_description": "Iconic Chennai seaside promenade known for sunrise views and street eats.",
        "rating": 4.4,
        "rating_count": 68000,
        "entry_fee": None,
        "is_featured": True,
        "address": "Kamarajar Salai, Chennai, Tamil Nadu",
    },
    {
        "name": "Ooty Botanical Gardens",
        "location": "Udhagamandalam (Ooty), Tamil Nadu",
        "state": "Tamil Nadu",
        "category": Category.NATURE,
        "description": (
            "Sprawling 55-acre terraced garden dating to 1848 with rare orchids, a fossilized tree trunk, "
            "and lush lawns. A classic stop on any Nilgiri hills itinerary."
        ),
        "short_description": "Historic 55-acre gardens in the Nilgiris with orchids and lawns.",
        "rating": 4.5,
        "rating_count": 27000,
        "entry_fee": 50.00,
        "address": "Vannarapettai, Ooty, Tamil Nadu",
    },
    {
        "name": "Kodaikanal Lake",
        "location": "Kodaikanal, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": Category.NATURE,
        "description": (
            "Star-shaped man-made lake at 2,000m elevation, ringed by a 5km cycling/boating path with misty views. "
            "Boating, cycling, and horse rides are popular."
        ),
        "short_description": "Star-shaped hill lake with boating and misty pine vistas.",
        "rating": 4.6,
        "rating_count": 19000,
        "entry_fee": None,
        "address": "Lake Rd, Kodaikanal, Tamil Nadu",
    },
    {
        "name": "Pichavaram Mangrove Forest",
        "location": "Cuddalore, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": Category.NATURE,
        "description": (
            "One of the world's largest mangrove ecosystems with narrow canoe channels, birdlife, and "
            "serene waterways connecting to the Bay of Bengal."
        ),
        "short_description": "Canoe through dense mangrove tunnels rich with birdlife.",
        "rating": 4.5,
        "rating_count": 8700,
        "entry_fee": 20.00,
        "address": "Pichavaram, Cuddalore, Tamil Nadu",
        "website": "",
    },
    {
        "name": "Rameswaram Ramanathaswamy Temple",
        "location": "Rameswaram, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": Category.RELIGIOUS,
        "description": (
            "Sacred Jyotirlinga temple famed for its 1,200m pillared corridor, sea-facing ghats, and "
            "connection to the Ramayana. A key Char Dham pilgrimage site."
        ),
        "short_description": "Jyotirlinga temple with India's longest corridor and seaside ghats.",
        "rating": 4.7,
        "rating_count": 36000,
        "entry_fee": None,
        "address": "Rameswaram, Ramanathapuram, Tamil Nadu",
    },
    {
        "name": "Mahabalipuram Shore Temple",
        "location": "Mahabalipuram, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": Category.HISTORY,
        "description": (
            "Pallava-era UNESCO site on the Bay of Bengal with twin shrines, rock-cut reliefs, and "
            "proximity to the famous Pancha Rathas and Arjuna's Penance."
        ),
        "short_description": "Seaside 8th-century granite temples and rock art complex.",
        "rating": 4.7,
        "rating_count": 24000,
        "entry_fee": 40.00,
        "address": "Mahabalipuram, Chengalpattu, Tamil Nadu",
    },
    {
        "name": "Sri Ranganathaswamy Temple",
        "location": "Srirangam, Tiruchirappalli, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": Category.RELIGIOUS,
        "description": (
            "Massive Vaishnavite temple on an island in the Cauvery with seven concentric prakaras, "
            "royal gopurams, and vibrant festivals."
        ),
        "short_description": "Island temple city with seven prakaras and towering gopurams.",
        "rating": 4.8,
        "rating_count": 41000,
        "entry_fee": None,
        "is_featured": False,
        "address": "Srirangam, Tiruchirappalli, Tamil Nadu",
    },
    {
        "name": "Mukurthi National Park",
        "location": "Nilgiris, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": Category.NATURE,
        "description": (
            "High-altitude shola-grassland reserve in the Western Ghats, habitat of the endangered "
            "Nilgiri tahr, with alpine lakes and trekking routes."
        ),
        "short_description": "Nilgiri shola grasslands home to the Nilgiri tahr.",
        "rating": 4.4,
        "rating_count": 3200,
        "entry_fee": 20.00,
        "address": "Mukurthi, Nilgiris, Tamil Nadu",
    },
]


class Command(BaseCommand):
    help = "Seed the database with sample Tamil Nadu tourist places."

    def handle(self, *args, **options):
        created = 0
        skipped = 0

        for data in SAMPLE_PLACES:
            _, was_created = TouristPlace.objects.get_or_create(
                name=data["name"],
                defaults=data,
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ Created: {data['name']}"))
            else:
                skipped += 1
                self.stdout.write(f"  – Skipped (exists): {data['name']}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone! Created {created} places, skipped {skipped} existing."
            )
        )
