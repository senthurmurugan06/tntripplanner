"""
TNTripPlanner - Production-grade Django settings.
Environment-based configuration with secure defaults.
"""

import os
from pathlib import Path

# ─── BASE ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# Try to load .env via python-decouple; fall back to os.environ
try:
    from decouple import config, Csv
    _config = config
    _csv = Csv
except ImportError:
    def _config(key, default=None, cast=None):
        val = os.environ.get(key, default)
        return cast(val) if (cast and val is not None) else val
    def _csv(val):
        return [v.strip() for v in val.split(",")] if val else []

# ─── SECURITY ─────────────────────────────────────────────────────────────────
SECRET_KEY = _config("SECRET_KEY", default="django-insecure-change-me-in-production-please")
DEBUG = _config("DEBUG", default=True, cast=bool)

def _comma_split(value):
    return [host.strip() for host in value.split(",") if host.strip()]

_vercel_url = os.environ.get("VERCEL_URL", "")
_vercel_hosts = [".vercel.app"] if _vercel_url else []
ALLOWED_HOSTS = _config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1" + ("," + ",".join(_vercel_hosts) if _vercel_hosts else ""),
    cast=_comma_split,
)

# ─── APPLICATIONS ─────────────────────────────────────────────────────────────
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]

LOCAL_APPS = [
    "apps.users.apps.UsersConfig",
    "apps.places.apps.PlacesConfig",
    "apps.chatbot.apps.ChatbotConfig",
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

# ─── MIDDLEWARE ────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "TNTripPlanner.urls"

# ─── TEMPLATES ────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
            ],
        },
    },
]

WSGI_APPLICATION = "TNTripPlanner.wsgi.application"

# ─── DATABASE ─────────────────────────────────────────────────────────────────
_db_engine = _config("DB_ENGINE", default="django.db.backends.sqlite3")

if _db_engine == "django.db.backends.postgresql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _config("DB_NAME", default="tntripplanner"),
            "USER": _config("DB_USER", default="postgres"),
            "PASSWORD": _config("DB_PASSWORD", default=""),
            "HOST": _config("DB_HOST", default="localhost"),
            "PORT": _config("DB_PORT", default="5432"),
            "OPTIONS": {
                "connect_timeout": 10,
            },
            "CONN_MAX_AGE": 60,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ─── AUTH ─────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = "users.CustomUser"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "places:list"
LOGOUT_REDIRECT_URL = "users:login"

# ─── INTERNATIONALISATION ─────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Chicago"
USE_I18N = True
USE_TZ = True

# ─── STATIC & MEDIA ───────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ─── DEFAULT PK ───────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─── COHERE AI ────────────────────────────────────────────────────────────
COHERE_API_KEY = _config("COHERE_API_KEY", default="")
COHERE_MODEL = _config("COHERE_MODEL", default="command-r-08-2024")
COHERE_MAX_TOKENS = int(_config("COHERE_MAX_TOKENS", default=500))
COHERE_TIMEOUT = int(_config("COHERE_TIMEOUT", default=30))

# ─── PAGINATION ───────────────────────────────────────────────────────────────
PLACES_PER_PAGE = int(_config("PLACES_PER_PAGE", default=9))

# ─── LOGGING ──────────────────────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": _config("DJANGO_LOG_LEVEL", default="WARNING"),
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}

# ─── PRODUCTION SECURITY HEADERS (only when DEBUG=False) ─────────────────────
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
