import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Flags básicas ---
SECRET_KEY = os.environ.get("SECRET_KEY")  # defina no Render
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# Ex.: "api-seuapp.onrender.com,localhost,127.0.0.1"
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()]

# --- Apps ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",

    "rest_framework",
    "corsheaders",

    "real_estate_lens",
]

# Debug toolbar só em dev
if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]

# --- Middleware ---
MIDDLEWARE = [
    # CORS precisa vir bem no topo
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise precisa vir antes de CommonMiddleware para estáticos em prod
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

ROOT_URLCONF = "setup.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "setup.wsgi.application"

# --- Database (Supabase PostGIS) ---
# Em Render defina DATABASE_URL = postgres://...supabase.co:5432/postgres?sslmode=require
db_cfg = dj_database_url.parse(
    os.environ["DATABASE_URL"],
    conn_max_age=600,
    ssl_require=True,
)
# Força o backend GIS
db_cfg["ENGINE"] = "django.contrib.gis.db.backends.postgis"
DATABASES = {"default": db_cfg}

# --- Password validators (mantidos) ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- I18N ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Static (WhiteNoise) ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    }
}

# --- Django REST Framework ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

# --- User model ---
AUTH_USER_MODEL = "real_estate_lens.User"

# --- Cache (ok manter locmem) ---
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# --- CORS/CSRF ---
# Defina FRONTEND_ORIGIN no Render/Netlify (ex.: https://seu-frontend.netlify.app)
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN")

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [FRONTEND_ORIGIN] if FRONTEND_ORIGIN else []

# CSRF requer hostname exato e HTTPS
CSRF_TRUSTED_ORIGINS = [
    "https://reallens-api.onrender.com",
]
if FRONTEND_ORIGIN:
    CSRF_TRUSTED_ORIGINS.append(FRONTEND_ORIGIN)
# BACKEND_ORIGIN opcional: ex.: https://api-seuapp.onrender.com
BACKEND_ORIGIN = os.environ.get("BACKEND_ORIGIN")
if BACKEND_ORIGIN:
    CSRF_TRUSTED_ORIGINS.append(BACKEND_ORIGIN)

# Em dev local:
if DEBUG:
    CORS_ALLOWED_ORIGINS += ["http://localhost:3000", "http://127.0.0.1:3000"]
    CSRF_TRUSTED_ORIGINS += ["http://localhost:3000", "http://127.0.0.1:3000"]

# --- Debug toolbar ips ---
INTERNAL_IPS = ["127.0.0.1"]

# --- Segurança para proxy/HTTPS do Render ---
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG

# Opcional endurecer:
SECURE_HSTS_SECONDS = 0 if DEBUG else 60 * 60 * 24  # comece baixo, aumente depois
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

# --- Default PK ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
