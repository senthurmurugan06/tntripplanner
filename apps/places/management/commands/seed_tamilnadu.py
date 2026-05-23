"""
Management command: seed_tamilnadu
Usage: python manage.py seed_tamilnadu

Populates the database with 50 authentic Tamil Nadu tourist places.
"""

from django.core.management.base import BaseCommand
from apps.places.models import TouristPlace, Category


# ── Category mapping from original data ──────────────────────────────────────
CAT_MAP = {
    "Temple":       Category.RELIGIOUS,
    "Beach":        Category.NATURE,
    "Garden":       Category.NATURE,
    "Hill Station": Category.NATURE,
    "Wildlife":     Category.NATURE,
    "Monument":     Category.HISTORY,
    "Fort":         Category.HISTORY,
    "Waterfall":    Category.NATURE,
    "Other":        Category.OTHER,
}

# ── 50 Tamil Nadu places ──────────────────────────────────────────────────────
TN_PLACES = [
    {
        "name": "Brihadeeswarar Temple",
        "location": "Thanjavur, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Temple",
        "short_description": "A UNESCO World Heritage Site and one of the largest temples in India.",
        "description": (
            "Built by Raja Raja Chola I in the 11th century, this temple is a marvel of Dravidian "
            "architecture and a UNESCO World Heritage Site. The temple tower is among the tallest "
            "of its kind in the world. Best time to visit: October to March. "
            "Timings: 6:00 AM – 12:30 PM, 4:00 PM – 8:30 PM. "
            "Nearby: Thanjavur Palace, Saraswathi Mahal Library. "
            "How to reach: ~2 km from Thanjavur railway station."
        ),
        "rating": 4.9, "rating_count": 38400,
        "entry_fee": None, "is_featured": True,
        "latitude": 10.7828, "longitude": 79.1310,
        "website": "",
    },
    {
        "name": "Meenakshi Amman Temple",
        "location": "Madurai, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Temple",
        "short_description": "A historic Hindu temple on the southern bank of the Vaigai River.",
        "description": (
            "Famed for its stunning architecture and towering gopurams, the Meenakshi Temple is "
            "dedicated to Goddess Meenakshi and Lord Sundareswarar. Best time: October to March. "
            "Timings: 5:00 AM – 12:30 PM, 4:00 PM – 10:00 PM. "
            "Nearby: Thirumalai Nayakkar Mahal, Gandhi Museum. "
            "Located in the heart of Madurai, easily accessible by road and rail."
        ),
        "rating": 4.8, "rating_count": 52100,
        "entry_fee": None, "is_featured": True,
        "latitude": 9.9195, "longitude": 78.1191,
    },
    {
        "name": "Kanyakumari Beach",
        "location": "Kanyakumari, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Beach",
        "short_description": "The southernmost tip of India, famous for sunrise and sunset views.",
        "description": (
            "Kanyakumari Beach is where the Bay of Bengal, Indian Ocean, and Arabian Sea meet. "
            "Known for its spectacular sunrise and sunset, especially on full moon days. "
            "Best time: October to March. Open all day. "
            "Nearby: Vivekananda Rock Memorial, Thiruvalluvar Statue. "
            "Well connected by train and bus."
        ),
        "rating": 4.7, "rating_count": 44300,
        "entry_fee": None, "is_featured": True,
        "latitude": 8.0883, "longitude": 77.5385,
    },
    {
        "name": "Ooty Botanical Gardens",
        "location": "Ooty, The Nilgiris, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Garden",
        "short_description": "A beautiful 55-acre garden in the hill station of Ooty.",
        "description": (
            "Spread over 55 acres, the Government Botanical Gardens in Ooty is home to thousands "
            "of exotic and indigenous plants, shrubs, ferns, and bonsai. "
            "Best time: April to June, September to November. "
            "Timings: 7:00 AM – 6:30 PM. Entry: ₹30 (adults), ₹15 (children). "
            "Nearby: Ooty Lake, Doddabetta Peak. "
            "Accessible by Nilgiri Mountain Railway and road."
        ),
        "rating": 4.5, "rating_count": 19800,
        "entry_fee": 1.00, "is_featured": True,
        "latitude": 11.4116, "longitude": 76.7031,
    },
    {
        "name": "Kodaikanal Lake",
        "location": "Kodaikanal, Dindigul, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Hill Station",
        "short_description": "A star-shaped man-made lake in the heart of Kodaikanal.",
        "description": (
            "Kodaikanal Lake is a popular tourist spot for boating, cycling, and horse riding. "
            "The lake is surrounded by lush greenery and hills. "
            "Best time: April to June, September to October. "
            "Timings: 6:00 AM – 5:00 PM. Free entry (boating extra). "
            "Nearby: Coaker's Walk, Bryant Park. "
            "Accessible by road from Madurai and Coimbatore."
        ),
        "rating": 4.6, "rating_count": 27500,
        "entry_fee": None, "is_featured": True,
        "latitude": 10.2381, "longitude": 77.4892,
    },
    {
        "name": "Ramanathaswamy Temple",
        "location": "Rameswaram, Ramanathapuram, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Temple",
        "short_description": "A sacred Jyotirlinga temple on Rameswaram island with the longest corridors.",
        "description": (
            "Ramanathaswamy Temple is one of the twelve Jyotirlinga temples and a major pilgrimage "
            "site. Its corridors are the longest among all Hindu temples in India. "
            "Best time: October to April. "
            "Timings: 5:00 AM – 1:00 PM, 3:00 PM – 9:00 PM. Free entry. "
            "Nearby: Dhanushkodi, Pamban Bridge. "
            "~2 km from Rameswaram railway station."
        ),
        "rating": 4.8, "rating_count": 35200,
        "entry_fee": None, "is_featured": False,
        "latitude": 9.2881, "longitude": 79.3174,
    },
    {
        "name": "Mahabalipuram Shore Temple",
        "location": "Mahabalipuram, Chengalpattu, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Monument",
        "short_description": "A UNESCO World Heritage 8th-century granite temple on the Coromandel Coast.",
        "description": (
            "The Shore Temple is a structural temple built with blocks of granite, dating from the "
            "8th century AD. Part of the Group of Monuments at Mahabalipuram, a UNESCO World "
            "Heritage Site. Best time: November to February. "
            "Timings: 6:00 AM – 6:00 PM. Entry: ₹40 (Indians), ₹600 (foreigners). "
            "Nearby: Pancha Rathas, Arjuna's Penance. "
            "60 km from Chennai, accessible by road."
        ),
        "rating": 4.6, "rating_count": 21400,
        "entry_fee": 2.00, "is_featured": False,
        "latitude": 12.6170, "longitude": 80.1994,
    },
    {
        "name": "Yercaud Lake",
        "location": "Yercaud, Salem, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Hill Station",
        "short_description": "A serene lake in the Shevaroy hills, ideal for boating.",
        "description": (
            "Yercaud Lake is surrounded by gardens and woods, offering boating and a peaceful "
            "atmosphere in the hill station of Yercaud. "
            "Best time: October to June. "
            "Timings: 9:00 AM – 5:30 PM. Free entry (boating extra). "
            "Nearby: Lady's Seat, Pagoda Point. "
            "30 km from Salem, accessible by road."
        ),
        "rating": 4.2, "rating_count": 9800,
        "entry_fee": None, "is_featured": False,
        "latitude": 11.7753, "longitude": 78.2096,
    },
    {
        "name": "Mudumalai National Park",
        "location": "The Nilgiris, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Wildlife",
        "short_description": "A famous tiger reserve home to elephants, leopards, and rare birds.",
        "description": (
            "Mudumalai is home to tigers, elephants, leopards, and many bird species. "
            "Part of the Nilgiri Biosphere Reserve. "
            "Best time: February to June, September to December. "
            "Timings: 6:00 AM – 6:00 PM. Entry: ₹30 (Indians), ₹300 (foreigners). "
            "Nearby: Bandipur National Park, Masinagudi. "
            "Accessible by road from Ooty (40 km) and Mysore (90 km)."
        ),
        "rating": 4.5, "rating_count": 14600,
        "entry_fee": 2.00, "is_featured": False,
        "latitude": 11.5983, "longitude": 76.5856,
    },
    {
        "name": "Courtallam Waterfalls",
        "location": "Tenkasi, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Waterfall",
        "short_description": 'Known as the "Spa of South India", famous for its medicinal waterfalls.',
        "description": (
            "Courtallam has nine waterfalls, each with unique charm. The water is believed to have "
            "medicinal properties due to herbs in the Western Ghats. "
            "Best time: June to September (monsoon). "
            "Timings: 6:00 AM – 8:00 PM. Free entry. "
            "Nearby: Five Falls, Old Courtallam. "
            "Tenkasi is the nearest railway station (7 km)."
        ),
        "rating": 4.4, "rating_count": 18300,
        "entry_fee": None, "is_featured": False,
        "latitude": 8.9216, "longitude": 77.2682,
    },
    {
        "name": "Vellore Fort",
        "location": "Vellore, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Fort",
        "short_description": "A 16th-century fort with a grand moat, ancient temples, church, and mosque.",
        "description": (
            "Vellore Fort is known for its grand ramparts, wide moat, and the Jalakandeswarar "
            "Temple inside. It also houses a church and a mosque. "
            "Best time: November to February. "
            "Timings: 8:00 AM – 6:00 PM. Free entry. "
            "Nearby: Golden Temple, Government Museum. "
            "Located in Vellore city center, well connected by road and rail."
        ),
        "rating": 4.3, "rating_count": 16700,
        "entry_fee": None, "is_featured": False,
        "latitude": 12.9187, "longitude": 79.1325,
    },
    {
        "name": "Pichavaram Mangrove Forest",
        "location": "Cuddalore, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Wildlife",
        "short_description": "One of the world's largest mangrove forests, ideal for boat rides.",
        "description": (
            "Pichavaram offers unique boat rides through mangrove channels and is a haven for "
            "birdwatchers. "
            "Best time: November to February. "
            "Timings: 8:00 AM – 5:00 PM. Entry: ₹5 (boating extra). "
            "Nearby: Chidambaram Nataraja Temple. "
            "15 km from Chidambaram, accessible by road."
        ),
        "rating": 4.4, "rating_count": 11200,
        "entry_fee": None, "is_featured": False,
        "latitude": 11.4281, "longitude": 79.7747,
    },
    {
        "name": "Kolli Hills",
        "location": "Namakkal, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Hill Station",
        "short_description": "A scenic hill station known for its hairpin bends and Agaya Gangai Falls.",
        "description": (
            "Kolli Hills is famous for its natural beauty, trekking trails, and the Agaya Gangai "
            "waterfall. "
            "Best time: February to December. "
            "Open all day. Free entry. "
            "Nearby: Agaya Gangai Falls, Arapaleeswarar Temple. "
            "45 km from Namakkal, accessible by road."
        ),
        "rating": 4.3, "rating_count": 7900,
        "entry_fee": None, "is_featured": False,
        "latitude": 11.2250, "longitude": 78.3200,
    },
    {
        "name": "Thiruvannamalai Arunachaleswarar Temple",
        "location": "Tiruvannamalai, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Temple",
        "short_description": "A grand Shiva temple at Arunachala hill, famous for Karthigai Deepam.",
        "description": (
            "One of the Pancha Bhoota Stalas representing fire, this ancient temple is dedicated "
            "to Lord Shiva. Famous for the Karthigai Deepam festival in November. "
            "Best time: November (festival), October to March. "
            "Timings: 5:30 AM – 12:30 PM, 3:30 PM – 9:30 PM. Free entry. "
            "Nearby: Arunachala Hill, Ramana Ashram. "
            "Well connected by road and rail."
        ),
        "rating": 4.7, "rating_count": 29400,
        "entry_fee": None, "is_featured": False,
        "latitude": 12.2253, "longitude": 79.0747,
    },
    {
        "name": "Hogenakkal Falls",
        "location": "Dharmapuri, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Waterfall",
        "short_description": 'The "Niagara of India", famous for scenic coracle rides.',
        "description": (
            "Hogenakkal Falls is a major tourist attraction with medicinal baths and boat rides "
            "in round coracles on the Kaveri River. "
            "Best time: July to October. "
            "Timings: 8:00 AM – 5:30 PM. Entry: ₹10 (boating extra). "
            "Nearby: Pennagaram, Melagiri Hills. "
            "46 km from Dharmapuri, accessible by road."
        ),
        "rating": 4.5, "rating_count": 22100,
        "entry_fee": None, "is_featured": False,
        "latitude": 12.1122, "longitude": 77.7750,
    },
    {
        "name": "Gingee Fort",
        "location": "Viluppuram, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Fort",
        "short_description": 'A massive hilltop fort complex known as the "Troy of the East".',
        "description": (
            "Gingee Fort is spread over three hillocks and is one of the most impregnable forts "
            "in India, built by the Nayak dynasty. "
            "Best time: November to February. "
            "Timings: 9:00 AM – 5:00 PM. Entry: ₹25 (Indians), ₹300 (foreigners). "
            "Nearby: Rajagiri, Krishnagiri, Chandrayandurg hills. "
            "37 km from Villupuram, accessible by road."
        ),
        "rating": 4.3, "rating_count": 8700,
        "entry_fee": 2.00, "is_featured": False,
        "latitude": 12.2541, "longitude": 79.4177,
    },
    {
        "name": "Kumbakonam Temples",
        "location": "Kumbakonam, Thanjavur, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Temple",
        "short_description": 'The "Temple Town" of Tamil Nadu with over 188 ancient temples.',
        "description": (
            "Kumbakonam is known as the 'temple town' with over 188 temples, including the famous "
            "Adi Kumbeswarar and Sarangapani temples. "
            "Best time: October to March. "
            "Timings: 6:00 AM – 12:00 PM, 4:00 PM – 9:00 PM. Free entry. "
            "Nearby: Mahamaham Tank, Airavatesvara Temple (UNESCO). "
            "Well connected by rail and road."
        ),
        "rating": 4.5, "rating_count": 13400,
        "entry_fee": None, "is_featured": False,
        "latitude": 10.9629, "longitude": 79.3887,
    },
    {
        "name": "Pulicat Lake",
        "location": "Thiruvallur, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Wildlife",
        "short_description": "India's second largest brackish water lake, a haven for flamingos.",
        "description": (
            "Pulicat Lake is the second largest brackish water lake in India and a haven for "
            "flamingos and other migratory birds. "
            "Best time: October to March. "
            "Timings: 6:00 AM – 6:00 PM. Free entry. "
            "Nearby: Pulicat Bird Sanctuary, Dutch Cemetery. "
            "60 km from Chennai, accessible by road."
        ),
        "rating": 4.1, "rating_count": 5600,
        "entry_fee": None, "is_featured": False,
        "latitude": 13.4141, "longitude": 80.3161,
    },
    {
        "name": "Vivekananda Rock Memorial",
        "location": "Kanyakumari, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Monument",
        "short_description": "A memorial built on the rock where Swami Vivekananda meditated.",
        "description": (
            "The Vivekananda Rock Memorial is built on a small island and is reached by ferry. "
            "It commemorates Swami Vivekananda's meditation and spiritual awakening. "
            "Best time: October to March. "
            "Timings: 8:00 AM – 4:00 PM. Entry: ₹20. "
            "Nearby: Thiruvalluvar Statue, Kanyakumari Beach. "
            "Ferry available from Kanyakumari jetty."
        ),
        "rating": 4.6, "rating_count": 31800,
        "entry_fee": 1.00, "is_featured": False,
        "latitude": 8.0798, "longitude": 77.5539,
    },
    {
        "name": "Kalrayan Hills",
        "location": "Kallakurichi, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Hill Station",
        "short_description": "A lesser-known hill station ideal for trekking and offbeat travel.",
        "description": (
            "Kalrayan Hills offer waterfalls, forests, and tribal villages, perfect for offbeat "
            "travel and nature lovers. "
            "Best time: October to March. "
            "Open all day. Free entry. "
            "Nearby: Periyar Falls, Gomukhi Dam. "
            "Nearest town is Kallakurichi, accessible by road."
        ),
        "rating": 4.0, "rating_count": 3200,
        "entry_fee": None, "is_featured": False,
        "latitude": 11.7000, "longitude": 78.7000,
    },
    {
        "name": "Kalakkad Mundanthurai Tiger Reserve",
        "location": "Tirunelveli, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Wildlife",
        "short_description": "A vast tiger reserve in the Western Ghats with rich biodiversity.",
        "description": (
            "This reserve is home to tigers, elephants, leopards, and many endemic species of "
            "flora and fauna in the Western Ghats. "
            "Best time: October to March. "
            "Timings: 6:00 AM – 6:00 PM. Entry: ₹20 (Indians), ₹200 (foreigners). "
            "Nearby: Manimuthar Falls, Papanasam Dam. "
            "Ambasamudram is the nearest town."
        ),
        "rating": 4.4, "rating_count": 6800,
        "entry_fee": 1.00, "is_featured": False,
        "latitude": 8.6500, "longitude": 77.4000,
    },
    {
        "name": "Sankagiri Fort",
        "location": "Salem, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Fort",
        "short_description": "A Vijayanagar-era fort with 14 walls and panoramic views.",
        "description": (
            "Sankagiri Fort is known for its strategic hilltop location and panoramic views "
            "of the surrounding landscape. Built during the Vijayanagar Empire. "
            "Best time: November to February. "
            "Timings: 9:00 AM – 5:00 PM. Entry: ₹25. "
            "Nearby: Sankari Durg, Bhavani Sagar Dam. "
            "38 km from Salem, accessible by road."
        ),
        "rating": 4.0, "rating_count": 4100,
        "entry_fee": 1.00, "is_featured": False,
        "latitude": 11.4481, "longitude": 77.8722,
    },
    {
        "name": "Kutralam Main Falls",
        "location": "Tenkasi, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Waterfall",
        "short_description": "The largest of Courtallam's falls, beloved for herbal monsoon baths.",
        "description": (
            "Kutralam Main Falls is the largest of the Courtallam falls, attracting thousands "
            "of visitors during the monsoon season for herbal water baths. "
            "Best time: June to September. "
            "Timings: 6:00 AM – 8:00 PM. Free entry. "
            "Nearby: Five Falls, Old Courtallam. "
            "7 km from Tenkasi, accessible by road."
        ),
        "rating": 4.5, "rating_count": 17600,
        "entry_fee": None, "is_featured": False,
        "latitude": 8.9216, "longitude": 77.2682,
    },
    {
        "name": "Guindy National Park",
        "location": "Chennai, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Wildlife",
        "short_description": "A rare national park within a city, home to blackbucks and deer.",
        "description": (
            "Guindy National Park is a green lung of Chennai, home to blackbucks, spotted deer, "
            "jackals, and diverse birdlife. Includes a children's park and snake park. "
            "Best time: November to February. "
            "Timings: 9:00 AM – 5:30 PM (closed Tuesdays). Entry: ₹20 (adults), ₹5 (children). "
            "Nearby: Snake Park, Anna University. "
            "Located within Chennai, accessible by road and rail."
        ),
        "rating": 4.2, "rating_count": 8900,
        "entry_fee": 1.00, "is_featured": False,
        "latitude": 13.0108, "longitude": 80.2340,
    },
    {
        "name": "Sathanur Dam",
        "location": "Tiruvannamalai, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "OTHER",
        "short_description": "A scenic dam on the Pennaiyar River with a crocodile park and gardens.",
        "description": (
            "Sathanur Dam is a popular picnic spot built across the Pennaiyar River. "
            "The surrounding park includes a crocodile enclosure and botanical garden. "
            "Best time: November to February. "
            "Timings: 8:00 AM – 5:00 PM. Entry: ₹10. "
            "Nearby: Crocodile Park, Botanical Garden. "
            "30 km from Tiruvannamalai, accessible by road."
        ),
        "rating": 4.0, "rating_count": 5400,
        "entry_fee": None, "is_featured": False,
        "latitude": 12.2567, "longitude": 78.9633,
    },
    {
        "name": "Muttukadu Boat House",
        "location": "Chengalpattu, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "OTHER",
        "short_description": "A popular water sports and boating destination near Chennai.",
        "description": (
            "Muttukadu offers rowing, water scooters, and windsurfing on the backwaters. "
            "A popular weekend getaway from Chennai. "
            "Best time: November to February. "
            "Timings: 9:00 AM – 6:00 PM. Entry: ₹10 (boating extra). "
            "Nearby: DakshinaChitra, Covelong Beach. "
            "36 km from Chennai on East Coast Road."
        ),
        "rating": 4.1, "rating_count": 7200,
        "entry_fee": None, "is_featured": False,
        "latitude": 12.8232, "longitude": 80.2412,
    },
    {
        "name": "Karaikudi Chettinad Mansions",
        "location": "Sivaganga, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "OTHER",
        "short_description": "Famous for grand heritage mansions, antique markets, and unique cuisine.",
        "description": (
            "Karaikudi is the heart of Chettinad, known for its palatial homes, antique markets, "
            "and spicy Chettinad cuisine. A must-visit for heritage lovers. "
            "Best time: November to February. "
            "Timings: 9:00 AM – 6:00 PM. Entry varies by mansion. "
            "Nearby: Athangudi Palace, Chettinad Museum. "
            "Well connected by rail and road."
        ),
        "rating": 4.4, "rating_count": 9100,
        "entry_fee": None, "is_featured": False,
        "latitude": 10.0667, "longitude": 78.7667,
    },
    {
        "name": "Siruvani Waterfalls",
        "location": "Coimbatore, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Waterfall",
        "short_description": "A scenic waterfall said to have the sweetest water in India.",
        "description": (
            "Siruvani Waterfalls is surrounded by dense forests and is a popular picnic spot "
            "known for its crystal-clear, naturally sweet water. "
            "Best time: June to October. "
            "Timings: 10:00 AM – 5:00 PM. Entry: ₹50. "
            "Nearby: Siruvani Dam, Kovai Kutralam Falls. "
            "35 km from Coimbatore, accessible by road."
        ),
        "rating": 4.4, "rating_count": 12300,
        "entry_fee": 3.00, "is_featured": False,
        "latitude": 11.0190, "longitude": 76.7397,
    },
    {
        "name": "Vandalur Zoo (Arignar Anna Zoological Park)",
        "location": "Chengalpattu, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "OTHER",
        "short_description": "One of the largest zoos in South Asia with 2,500+ animals.",
        "description": (
            "Vandalur Zoo houses over 2,500 animals across 1,265 acres and is a major attraction "
            "for families. Part of the Vandalur Reserve Forest. "
            "Best time: November to February. "
            "Timings: 9:00 AM – 5:00 PM (closed Tuesdays). Entry: ₹50 (adults), ₹20 (children). "
            "Nearby: Vandalur Reserve Forest. "
            "31 km from Chennai, accessible by road and suburban train."
        ),
        "rating": 4.3, "rating_count": 24600,
        "entry_fee": 3.00, "is_featured": False,
        "latitude": 12.8925, "longitude": 80.0807,
    },
    {
        "name": "Thanjavur Maratha Palace",
        "location": "Thanjavur, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Monument",
        "short_description": "Historic palace complex with art gallery and Saraswathi Mahal Library.",
        "description": (
            "The palace was built by the Marathas and Nayaks and houses a museum, library, and "
            "art gallery with rare manuscripts. "
            "Best time: October to March. "
            "Timings: 9:00 AM – 5:30 PM. Entry: ₹50. "
            "Nearby: Brihadeeswarar Temple, Schwartz Church. "
            "Located in Thanjavur city."
        ),
        "rating": 4.3, "rating_count": 8400,
        "entry_fee": 3.00, "is_featured": False,
        "latitude": 10.7867, "longitude": 79.1378,
    },
    {
        "name": "Kanchipuram Temples",
        "location": "Kanchipuram, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Temple",
        "short_description": 'The "City of Thousand Temples", famous for silk sarees.',
        "description": (
            "Kanchipuram is famous for its ancient temples like Ekambareswarar, Kailasanathar, "
            "and Kamakshi Amman. Also renowned for its handwoven silk sarees. "
            "Best time: October to March. "
            "Timings: 6:00 AM – 12:00 PM, 4:00 PM – 8:00 PM. Free entry. "
            "Nearby: Silk Saree Weaving Centers. "
            "Well connected by road and rail from Chennai (75 km)."
        ),
        "rating": 4.5, "rating_count": 18700,
        "entry_fee": None, "is_featured": False,
        "latitude": 12.8342, "longitude": 79.7036,
    },
    {
        "name": "Palaruvi Waterfalls",
        "location": "Tirunelveli, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Waterfall",
        "short_description": 'A beautiful waterfall on the Tamil Nadu–Kerala border ("stream of milk").',
        "description": (
            "Palaruvi means 'stream of milk' and is a popular picnic spot, especially during the "
            "monsoon. The falls cascade from a height of about 60 metres. "
            "Best time: June to September. "
            "Timings: 8:00 AM – 5:00 PM. Entry: ₹25. "
            "Nearby: Thenmala Dam, Courtallam Falls. "
            "75 km from Tirunelveli, accessible by road."
        ),
        "rating": 4.3, "rating_count": 7600,
        "entry_fee": 2.00, "is_featured": False,
        "latitude": 8.9600, "longitude": 77.1000,
    },
    {
        "name": "Chidambaram Nataraja Temple",
        "location": "Cuddalore, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Temple",
        "short_description": "Major Shaivite temple dedicated to Lord Nataraja, the cosmic dancer.",
        "description": (
            "Chidambaram Temple is an architectural marvel and a major pilgrimage site. "
            "One of the Pancha Bhoota Stalas representing space (Akasha). "
            "Best time: December to February. "
            "Timings: 6:00 AM – 12:00 PM, 5:00 PM – 10:00 PM. Free entry. "
            "Nearby: Pichavaram Mangroves, Thillai Kali Temple. "
            "Well connected by rail and road."
        ),
        "rating": 4.6, "rating_count": 22300,
        "entry_fee": None, "is_featured": False,
        "latitude": 11.3991, "longitude": 79.6937,
    },
    {
        "name": "Dhanushkodi",
        "location": "Ramanathapuram, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "OTHER",
        "short_description": "A haunting ghost town at the tip of Rameswaram island.",
        "description": (
            "Dhanushkodi was destroyed in the 1964 cyclone and is now a popular tourist spot "
            "for its haunting ruins, pristine beach, and mythological significance as the "
            "starting point of Rama's bridge to Lanka. "
            "Best time: October to March. "
            "Timings: 6:00 AM – 6:00 PM. Free entry. "
            "Nearby: Ramanathaswamy Temple, Pamban Bridge. "
            "18 km from Rameswaram, accessible by road."
        ),
        "rating": 4.5, "rating_count": 19400,
        "entry_fee": None, "is_featured": False,
        "latitude": 9.2722, "longitude": 79.4786,
    },
    {
        "name": "Masilamani Nathar Temple",
        "location": "Nagapattinam, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Temple",
        "short_description": "A 14th-century coastal temple blending Chinese and Tamil architecture.",
        "description": (
            "This temple is a blend of Chinese and Tamil architecture, built in 1306, partly "
            "submerged by the sea. Located on the Bay of Bengal coast. "
            "Best time: November to February. "
            "Timings: 6:00 AM – 12:00 PM, 4:00 PM – 8:00 PM. Free entry. "
            "Nearby: Velankanni Church, Nagore Dargah. "
            "20 km from Nagapattinam, accessible by road."
        ),
        "rating": 4.1, "rating_count": 4200,
        "entry_fee": None, "is_featured": False,
        "latitude": 11.0272, "longitude": 79.8583,
    },
    {
        "name": "Vellimalai Murugan Temple",
        "location": "Kanyakumari, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Temple",
        "short_description": "One of the six abodes of Lord Murugan with panoramic Western Ghats views.",
        "description": (
            "Vellimalai is one of the six abodes (Arupadai Veedu) of Lord Murugan and offers "
            "panoramic views of the Western Ghats. "
            "Best time: October to March. "
            "Timings: 6:00 AM – 12:00 PM, 4:00 PM – 8:00 PM. Free entry. "
            "Nearby: Padmanabhapuram Palace, Thirparappu Falls. "
            "50 km from Nagercoil, accessible by road."
        ),
        "rating": 4.3, "rating_count": 6100,
        "entry_fee": None, "is_featured": False,
        "latitude": 8.3000, "longitude": 77.3500,
    },
    # ── Additional classic Tamil Nadu destinations ──────────────────────────
    {
        "name": "Marina Beach",
        "location": "Chennai, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Beach",
        "short_description": "The world's second longest natural urban beach, stretching 13 km.",
        "description": (
            "Marina Beach in Chennai is the world's second longest natural urban beach, stretching "
            "about 13 kilometres. A beloved hangout for locals and tourists alike, the beach is lined "
            "with food stalls, statues, and historic buildings. "
            "Best time: November to February. "
            "Open all day. Free entry. "
            "Nearby: Kapaleeshwarar Temple, Fort St. George. "
            "Located in central Chennai, easily accessible by road and rail."
        ),
        "rating": 4.4, "rating_count": 68000,
        "entry_fee": None, "is_featured": True,
        "latitude": 13.0500, "longitude": 80.2824,
    },
    {
        "name": "Velankanni Basilica",
        "location": "Nagapattinam, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Temple",
        "short_description": 'The "Lourdes of the East", a famous Catholic pilgrimage centre.',
        "description": (
            "The Basilica of Our Lady of Good Health in Velankanni is one of India's most visited "
            "Catholic shrines and a place of harmony between faiths. "
            "Best time: September (feast season). "
            "Open all day. Free entry. "
            "Nearby: Nagapattinam coast, Nagore Dargah. "
            "Well connected by road and rail."
        ),
        "rating": 4.7, "rating_count": 41200,
        "entry_fee": None, "is_featured": False,
        "latitude": 10.6809, "longitude": 79.8467,
    },
    {
        "name": "Pamban Bridge",
        "location": "Rameswaram, Ramanathapuram, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Monument",
        "short_description": "India's first sea bridge, connecting Rameswaram island to the mainland.",
        "description": (
            "The Pamban Bridge is a railway bridge that connects Rameswaram island to the mainland. "
            "It was India's first sea bridge and is still an engineering marvel. The road bridge "
            "alongside it is equally breathtaking. "
            "Best time: October to March. "
            "Viewable anytime. "
            "Nearby: Ramanathaswamy Temple, Dhanushkodi. "
            "Accessible from Rameswaram town."
        ),
        "rating": 4.5, "rating_count": 23700,
        "entry_fee": None, "is_featured": False,
        "latitude": 9.2834, "longitude": 79.2095,
    },
    {
        "name": "Valparai Hill Station",
        "location": "Coimbatore, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Hill Station",
        "short_description": "A serene tea plantation hill station with 40 hairpin bends.",
        "description": (
            "Valparai is a scenic hill station in the Anamalai Hills, known for its lush tea and "
            "coffee estates. The drive up with 40 hairpin bends is an experience in itself. "
            "Best time: October to March. "
            "Open all day. "
            "Nearby: Anamalai Tiger Reserve, Monkey Falls. "
            "65 km from Coimbatore, accessible by road."
        ),
        "rating": 4.5, "rating_count": 11800,
        "entry_fee": None, "is_featured": False,
        "latitude": 10.3276, "longitude": 76.9509,
    },
    {
        "name": "Thiruparankundram Murugan Temple",
        "location": "Madurai, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Temple",
        "short_description": "One of the six abodes of Lord Murugan, carved into a rock hill.",
        "description": (
            "Thiruparankundram is one of the six abodes (Arupadai Veedu) of Lord Murugan, "
            "a significant rock-cut cave temple near Madurai. "
            "Best time: October to March. "
            "Timings: 5:30 AM – 12:30 PM, 4:00 PM – 9:00 PM. Free entry. "
            "Nearby: Madurai Meenakshi Temple, Alagar Kovil. "
            "8 km from Madurai, accessible by road."
        ),
        "rating": 4.5, "rating_count": 16400,
        "entry_fee": None, "is_featured": False,
        "latitude": 9.8786, "longitude": 78.0584,
    },
    {
        "name": "Coonoor Tea Gardens",
        "location": "Coonoor, The Nilgiris, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Garden",
        "short_description": "The second largest hill station in the Nilgiris with scenic tea estates.",
        "description": (
            "Coonoor is famous for its scenic tea plantations and the unique Nilgiri tea. "
            "The town offers beautiful views, trekking trails, and heritage train rides on the "
            "Nilgiri Mountain Railway. "
            "Best time: October to March. "
            "Open all day. "
            "Nearby: Sim's Park, Lamb's Rock, Ooty (18 km). "
            "Accessible by the famous toy train and road."
        ),
        "rating": 4.5, "rating_count": 14200,
        "entry_fee": None, "is_featured": False,
        "latitude": 11.3527, "longitude": 76.7950,
    },
    {
        "name": "Fort St. George",
        "location": "Chennai, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Fort",
        "short_description": "India's first English fortress, built by the British East India Company in 1644.",
        "description": (
            "Fort St. George was built in 1644 and is India's first English fortress. It now houses "
            "the Tamil Nadu Legislative Assembly and a museum displaying British-era artefacts. "
            "Best time: November to February. "
            "Timings: 9:00 AM – 5:00 PM (closed Fridays). Entry: ₹15. "
            "Nearby: Marina Beach, Kapaleeshwarar Temple. "
            "Located in central Chennai."
        ),
        "rating": 4.3, "rating_count": 10700,
        "entry_fee": 1.00, "is_featured": False,
        "latitude": 13.0804, "longitude": 80.2874,
    },
    {
        "name": "Nilgiri Mountain Railway",
        "location": "Ooty, The Nilgiris, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "OTHER",
        "short_description": "A UNESCO World Heritage toy train through the stunning Nilgiri hills.",
        "description": (
            "The Nilgiri Mountain Railway is a UNESCO World Heritage Site, one of the steepest "
            "rack railways in Asia. The toy train from Mettupalayam to Ooty passes through lush "
            "forests and 16 tunnels. "
            "Best time: October to March. "
            "Train schedule: check Indian Railways. Entry: ₹40–₹200+ depending on class. "
            "Nearby: Coonoor, Ooty Lake. "
            "Departure from Mettupalayam."
        ),
        "rating": 4.7, "rating_count": 28900,
        "entry_fee": 3.00, "is_featured": True,
        "latitude": 11.4102, "longitude": 76.6950,
    },
    {
        "name": "Padmanabhapuram Palace",
        "location": "Kanyakumari, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Monument",
        "short_description": "A magnificent 16th-century wooden palace, the largest in India.",
        "description": (
            "Padmanabhapuram Palace is the largest wooden palace complex in India, built in the "
            "16th century by the Travancore royal family. It features remarkable Kerala-style "
            "architecture with intricately carved woodwork. "
            "Best time: October to March. "
            "Timings: 9:00 AM – 5:00 PM (closed Mondays). Entry: ₹30 (Indians), ₹300 (foreigners). "
            "Nearby: Kanyakumari Beach, Vivekananda Rock. "
            "55 km from Kanyakumari."
        ),
        "rating": 4.5, "rating_count": 12100,
        "entry_fee": 2.00, "is_featured": False,
        "latitude": 8.2503, "longitude": 77.3214,
    },
    {
        "name": "Yelagiri Hills",
        "location": "Tirupathur, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Hill Station",
        "short_description": "A tranquil hill station with fruit orchards, rose gardens, and trekking.",
        "description": (
            "Yelagiri is a quiet hill station known for its orchards, rose gardens, paragliding, "
            "and trekking to Swamimalai Hill. A peaceful retreat from Chennai. "
            "Best time: November to February. "
            "Open all day. Free entry. "
            "Nearby: Swamimalai Hill, Jalagamparai Falls. "
            "165 km from Chennai, accessible by road."
        ),
        "rating": 4.2, "rating_count": 8300,
        "entry_fee": None, "is_featured": False,
        "latitude": 12.5823, "longitude": 78.6454,
    },
    {
        "name": "Thirukadaiyur Amirthakadeshwarar Temple",
        "location": "Nagapattinam, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Temple",
        "short_description": "Famous for the Abishekam ritual performed to conquer death and old age.",
        "description": (
            "Thirukadaiyur is one of the Paadal Petra Sthalangal shrines. It is especially "
            "famous for the Shashtiabdapoorthy and Sadhabhishekam rituals performed here for "
            "longevity and victory over death. "
            "Best time: October to March. "
            "Timings: 6:00 AM – 12:00 PM, 4:00 PM – 9:00 PM. Free entry. "
            "Nearby: Velankanni Basilica, Karaikal. "
            "30 km from Nagapattinam."
        ),
        "rating": 4.4, "rating_count": 9700,
        "entry_fee": None, "is_featured": False,
        "latitude": 11.0964, "longitude": 79.8519,
    },
    {
        "name": "Anamalai Tiger Reserve",
        "location": "Coimbatore, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Wildlife",
        "short_description": "A rich tiger reserve in the Anamalai hills with elephant safaris.",
        "description": (
            "Anamalai Tiger Reserve, formerly known as Indira Gandhi Wildlife Sanctuary, is home "
            "to tigers, elephants, leopards, and gaur. Elephant safaris are its highlight. "
            "Best time: February to June. "
            "Timings: 7:00 AM – 6:00 PM. Entry: ₹30 (Indians), ₹300 (foreigners). "
            "Nearby: Valparai, Monkey Falls. "
            "85 km from Coimbatore, accessible by road."
        ),
        "rating": 4.5, "rating_count": 10900,
        "entry_fee": 2.00, "is_featured": False,
        "latitude": 10.4000, "longitude": 77.0500,
    },
    {
        "name": "Kapaleeshwarar Temple",
        "location": "Chennai, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Temple",
        "short_description": "A magnificent Dravidian-style temple in the heart of Chennai.",
        "description": (
            "Kapaleeshwarar Temple in Mylapore is a landmark of Chennai, dedicated to Lord Shiva. "
            "Built in the Dravidian style with a towering gopuram, it is one of the most visited "
            "temples in the city. "
            "Best time: November to February. "
            "Timings: 5:00 AM – 12:00 PM, 4:00 PM – 9:00 PM. Free entry. "
            "Nearby: Marina Beach, San Thome Cathedral. "
            "Located in Mylapore, Chennai."
        ),
        "rating": 4.6, "rating_count": 31500,
        "entry_fee": None, "is_featured": False,
        "latitude": 13.0339, "longitude": 80.2692,
    },
    {
        "name": "Papanasam Beach",
        "location": "Tirunelveli, Tamil Nadu",
        "state": "Tamil Nadu",
        "category": "Beach",
        "short_description": "A scenic beach where the Tamirabarani River meets the sea.",
        "description": (
            "Papanasam Beach is known for its pristine beauty and the confluence of the "
            "Tamirabarani River with the Bay of Bengal. It has religious significance and "
            "is a serene alternative to busier beaches. "
            "Best time: November to March. "
            "Open all day. Free entry. "
            "Nearby: Tiruchendur Murugan Temple, Manapad. "
            "20 km from Tirunelveli."
        ),
        "rating": 4.2, "rating_count": 6800,
        "entry_fee": None, "is_featured": False,
        "latitude": 8.5167, "longitude": 78.1000,
    },
]


class Command(BaseCommand):
    help = "Seed the database with 50 authentic Tamil Nadu tourist places."

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("\n🏛️  Seeding Tamil Nadu tourist places...\n"))
        created = 0
        skipped = 0

        for data in TN_PLACES:
            # Map category string → Category enum value
            raw_cat = data.pop("category", "OTHER").strip()
            category = CAT_MAP.get(raw_cat, Category.OTHER)

            defaults = {
                "location":          data["location"],
                "state":             data["state"],
                "category":          category,
                "description":       data["description"],
                "short_description": data["short_description"],
                "rating":            data["rating"],
                "rating_count":      data["rating_count"],
                "entry_fee":         data.get("entry_fee"),
                "is_featured":       data.get("is_featured", False),
                "is_active":         True,
                "latitude":          data.get("latitude"),
                "longitude":         data.get("longitude"),
                "website":           data.get("website", ""),
            }

            _, was_created = TouristPlace.objects.get_or_create(
                name=data["name"],
                defaults=defaults,
            )

            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓  Added : {data['name']}"))
            else:
                skipped += 1
                self.stdout.write(f"  –  Exists: {data['name']}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅  Done! Added {created} Tamil Nadu places, skipped {skipped} existing.\n"
            )
        )
