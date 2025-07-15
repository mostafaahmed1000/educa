import os
from .base import *

DEBUG = False
ADMINS = [
    ("admin", "admin@admin.com"),
]
ALLOWED_HOSTS = ["*"]
DATABASES = {
# "default": {
#    'ENGINE': 'django.db.backends.postgresql',
#    'NAME': os.environ.get('POSTGRES_DB'),
#    'USER': os.environ.get('POSTGRES_USER'),
#    'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
#    'HOST': 'db',
#    'PORT': 5432,
#    }
    "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
REDIS_URL = 'redis://cache:6379'
CACHES['default']['LOCATION'] = REDIS_URL
CHANNEL_LAYERS['default']['CONFIG']['hosts'] = [REDIS_URL]

#Security
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

CORS_ALLOW_ALL_ORIGINS = False
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://frontend:3000",
]