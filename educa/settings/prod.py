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