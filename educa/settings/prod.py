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