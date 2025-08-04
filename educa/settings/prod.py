import os
from .base import *

DEBUG = False
ADMINS = [
    ("admin", "admin@admin.com"),
]
ALLOWED_HOSTS = ["*"]

REDIS_URL = 'redis://cache:6379'
CACHES['default']['LOCATION'] = REDIS_URL
CHANNEL_LAYERS['default']['CONFIG']['hosts'] = [REDIS_URL]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",         
    "http://51.20.193.62/",
    "http://13.60.24.37/",
]

CORS_ALLOW_CREDENTIALS = True