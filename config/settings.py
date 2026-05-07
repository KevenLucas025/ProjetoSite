from pathlib import Path
import os
from typing import cast
import dj_database_url
from dotenv import load_dotenv
import ssl

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

DEBUG = os.environ.get("DEBUG", "True") == "True" 

if DEBUG:
    EMAIL_BACKEND = "portfolio.email_backend.CustomEmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = "apikey"

EMAIL_HOST_PASSWORD = os.environ.get("SENDGRID_API_KEY", "")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

DEFAULT_FROM_EMAIL = "meusitepessoal2027@outlook.com"


SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-dev-key")


ALLOWED_HOSTS = [host.strip() for host in os.environ.get(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost"
).split(",")]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'portfolio',
    'django.contrib.sitemaps',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES: dict[str, dict[str, object]] = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    DATABASES['default'] = cast(
        dict[str, object],
        dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    )

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if not DEBUG:
    X_FRAME_OPTIONS = 'DENY'
    SECURE_CONTENT_TYPE_NOSNIFF = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # SECURE_SSL_REDIRECT = True
    # SECURE_HSTS_SECONDS = 3600