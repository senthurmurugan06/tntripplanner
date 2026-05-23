# 🏔️ TNTripPlanner

**Production-grade Django web application for Tamil Nadu tourism planning.**  
AI-powered chatbot · Tourist place discovery · User favorites · Clean architecture

---

## Architecture Overview

```
TNTripPlanner/
├── TNTripPlanner/          # Project config (settings, root URLs, wsgi)
├── apps/
│   ├── users/              # Custom auth: registration, login, profile
│   ├── places/             # Tourist places: CRUD, search, filter, favorites
│   └── chatbot/            # AI travel guide powered by Cohere
├── templates/              # Django template inheritance tree
│   ├── base.html           # Root layout (navbar, footer, toasts)
│   ├── users/              # Auth templates
│   ├── places/             # Place list + detail
│   └── chatbot/            # Async chat UI
├── static/
│   └── css/main.css        # Tamil Nadu heritage theme (CSS variables)
├── media/                  # User-uploaded images
├── requirements.txt
├── .env.example
└── manage.py
```

### Design Principles

- **Thin views** — all business logic in `services.py` per app
- **N+1 free** — `select_related`/`prefetch_related` on every queryset
- **Service layer** — Cohere AI calls fully encapsulated in `chatbot/services.py`
- **Env-based config** — no secrets in code; graceful fallback without `python-decouple`
- **Indexed fields** — `name`, `location`, `category`, `is_active`, timestamps
- **CSRF protection** — Django middleware + `X-CSRFToken` header on Fetch calls

---

## Quick Start

### 1. Clone & virtual environment

```bash
git clone <repo>
cd TNTripPlanner
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment variables

```bash
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY and GEMINI_API_KEY
```

### 3. Database & migrations

### 4. Images for places

Some of the sample places shipped with the project don’t include an
`image` field, so pages would otherwise show a generic placeholder. The
application now handles missing pictures gracefully in two ways:

1. **Runtime fallback** – `TouristPlace.image_url` will return an
   Unsplash random-photo URL based on the place name if no image is
   uploaded.  Try adding a place called “Brihadeeswarar Temple” and you’ll
   immediately see a relevant photo on the list/detail pages.
2. **Permanent download** – a new management command can fetch and save
   real images from Unsplash for any records lacking them:
   ```bash
   python manage.py fetch_place_images      # downloads and stores images
   python manage.py fetch_place_images --dry-run  # show what would happen
   ```
   The command is located at
   `apps/places/management/commands/fetch_place_images.py` and uses the
   place’s name/location to form the search query.  You can modify it to
   use other sources (Google Gemini image APIs, Google, etc.) if desired.

Administrators may also upload or replace images manually via the Django
admin interface (`/admin/apps/places/touristplace/`).


### 3. Database & migrations

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_places        # loads 9 sample TN destinations
```

### 4. Run

```bash
python manage.py runserver
# → http://127.0.0.1:8000/
```

---

## Key Features

### Tourist Places
- Paginated card grid (9 per page, configurable)
- Case-insensitive search across name, location, description
- Category filtering (9 categories)
- Sort by rating, name, newest, featured
- One-click favorites via async Fetch API (no page reload)
- Featured places highlighted in hero section
- SEO-friendly slugs, indexed fields, optimised queries

### AI Chatbot
- GPT-4o-mini powered Tamil Nadu travel guide
- Async Fetch API — no page reload, typing indicator
- Chat history stored per user (indexed timestamps)
- Graceful fallback when API key not configured
- Related tourist place detection and linking
- CSRF protection on JSON endpoint
- Message length validation (1000 char limit)

### Users
- Custom `AbstractUser` with avatar + bio
- Email uniqueness enforced at form and DB level
- Django's built-in password validators
- `LoginRequiredMixin` on all protected views
- Profile with favorites count + chat stats

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | (insecure dev key) | Django secret key — **change in production** |
| `DEBUG` | `True` | Set `False` in production |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed hosts; include your Vercel domain in production |
| `DB_ENGINE` | SQLite | `django.db.backends.postgresql` for Postgres |
| `DB_NAME` | `tntripplanner` | PostgreSQL database name |
| `DB_USER` | `postgres` | PostgreSQL user |
| `DB_PASSWORD` | *(empty)* | PostgreSQL password |
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `GEMINI_API_KEY` | *(empty)* | Google Gemini API key — chatbot works in fallback mode without it |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Gemini model |
| `GEMINI_MAX_TOKENS` | `500` | Max tokens per response |
| `GEMINI_TIMEOUT` | `30` | Request timeout (seconds) |
| `PLACES_PER_PAGE` | `9` | Pagination page size |

---

## Running Tests

```bash
python manage.py test apps.users apps.places apps.chatbot -v 2
```

For coverage:
```bash
pip install coverage
coverage run manage.py test apps
coverage report
coverage html   # view in browser: htmlcov/index.html
```

---

## Production Deployment

### Environment
```bash
DEBUG=False
SECRET_KEY=<strong-random-key>
ALLOWED_HOSTS=localhost,127.0.0.1,tntripplanner.vercel.app
DB_ENGINE=django.db.backends.postgresql
# ... other DB vars
```

### Collect static files
```bash
python manage.py collectstatic --noinput
```

### Gunicorn
```bash
gunicorn TNTripPlanner.wsgi:application \
  --workers 3 \
  --bind 0.0.0.0:8000 \
  --timeout 60 \
  --log-level info
```

### Security headers  
When `DEBUG=False`, the following are automatically enabled:
- `SECURE_HSTS_SECONDS` (1 year)
- `SECURE_SSL_REDIRECT`
- `SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE`
- `X_FRAME_OPTIONS = "DENY"`

---

## API Endpoints

| Method | URL | Auth | Description |
|---|---|---|---|
| `GET` | `/places/` | Public | List + search places |
| `GET` | `/places/<slug>/` | Public | Place detail |
| `POST` | `/places/<slug>/favorite/` | Required | Toggle favorite (JSON) |
| `GET` | `/chatbot/` | Required | Chat UI |
| `POST` | `/chatbot/send/` | Required | Send message (JSON) |
| `POST` | `/chatbot/clear/` | Required | Clear history |
| `GET` | `/users/register/` | Guest | Registration |
| `GET` | `/users/login/` | Guest | Login |
| `POST` | `/users/logout/` | Required | Logout |
| `GET` | `/users/profile/` | Required | View profile |
| `GET` | `/users/profile/edit/` | Required | Edit profile |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.x |
| Database | SQLite (dev) / PostgreSQL (prod) |
| AI | Google Gemini 1.5 Flash |
| Frontend | Bootstrap 5.3 + Custom CSS |
| Fonts | Playfair Display + DM Sans |
| Icons | Bootstrap Icons |
| Auth | Django built-in + AbstractUser |
| Images | Pillow |
| Config | python-decouple |
| Server | Gunicorn |
