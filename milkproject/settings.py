import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────
# SECURITY
# ─────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-please')
DEBUG = False

ALLOWED_HOSTS = [
    'milkbill.onrender.com',
    'localhost',
    '127.0.0.1',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ─────────────────────────────
# APPLICATIONS
# ─────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'accounts',
]

# ─────────────────────────────
# MIDDLEWARE
# ─────────────────────────────
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

# ─────────────────────────────
# URLS / WSGI
# ─────────────────────────────
ROOT_URLCONF = 'milkproject.urls'
WSGI_APPLICATION = 'milkproject.wsgi.application'

# ─────────────────────────────
# TEMPLATES
# ─────────────────────────────
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

# ─────────────────────────────
# DATABASE (SAFE FOR RENDER + LOCAL)
# ─────────────────────────────
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600,
        ssl_require=True
    )
}

# ─────────────────────────────
# PASSWORD VALIDATION
# ─────────────────────────────
AUTH_PASSWORD_VALIDATORS = []

# ─────────────────────────────
# INTERNATIONALIZATION
# ─────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ─────────────────────────────
# STATIC & MEDIA FILES
# ─────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Safe whitenoise storage (NO manifest crash)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ─────────────────────────────
# AUTH REDIRECTS
# ─────────────────────────────
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'accounts:home'
LOGOUT_REDIRECT_URL = 'login'

# ─────────────────────────────
# CSRF (REQUIRED FOR RENDER HTTPS)
# ─────────────────────────────
CSRF_TRUSTED_ORIGINS = [
    'https://milkbill.onrender.com',
]

# ─────────────────────────────
# TWILIO (OPTIONAL)
# ─────────────────────────────
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_NUMBER = os.environ.get(
    'TWILIO_WHATSAPP_NUMBER',
    'whatsapp:+14155238886'
)

# ─────────────────────────────
# DEFAULT FIELD
# ─────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
