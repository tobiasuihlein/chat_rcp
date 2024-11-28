from .base import *

DEBUG = True
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1'
]

# Static files settings
STATIC_ROOT = '/app/staticfiles'
STATIC_URL = 'static/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'