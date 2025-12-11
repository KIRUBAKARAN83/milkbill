import os
from pathlib import Path
from urllib.parse import urlparse
from decimal import Decimal

BASE_DIR = Path(milkbill).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-please')
DEBUG = FALSE

# ALLOWED_HOSTS from env or sensible defaults
ALLOWED_HOSTS = ['localhost','https://milkbill.onrender.com']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'milkproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Pricing from environment (fallback 50.0)
PRICE_PER_LITRE = float(os.environ.get('PRICE_PER_LITRE', '50.0'))

WSGI_APPLICATION = 'milkproject.wsgi.application'

# DATABASE configuration: use DATABASE_URL when provided (Postgres on Render)
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    parsed = urlparse(DATABASE_URL)
    scheme = parsed.scheme.split('+')[0]  # handle scheme variants

    if scheme in ('sqlite',):
        db_path = parsed.path or ''
        if db_path.startswith('/'):
            db_path = db_path.lstrip('/')
        db_name = BASE_DIR / db_path if db_path else BASE_DIR / 'db.sqlite3'
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': str(db_name),
            }
        }
    else:
        engine = 'django.db.backends.postgresql' if scheme in ('postgres', 'postgresql', 'psql') else (
                 'django.db.backends.mysql' if scheme.startswith('mysql') else 'django.db.backends.postgresql')
        DATABASES = {
            'default': {
                'ENGINE': engine,
                'NAME': parsed.path.lstrip('/') if parsed.path else '',
                'USER': parsed.username or '',
                'PASSWORD': parsed.password or '',
                'HOST': parsed.hostname or '',
                'PORT': parsed.port or '',
                'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', 600)),
                'OPTIONS': {'sslmode': os.environ.get('DB_SSLMODE', 'require')},
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Twilio / external service placeholders (set in Render env)
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

# Security settings helpful on Render
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if os.environ.get('CSRF_TRUSTED_ORIGINS') else []

# Login redirects
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'accounts:home'
LOGOUT_REDIRECT_URL = 'login'
