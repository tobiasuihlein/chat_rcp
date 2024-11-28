from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    'tobiasuihlein.de',
    'www.tobiasuihlein.de',
    '138.201.135.222', # Server IP
    '10.0.10.200', # Server-Proxy IP
    '10.0.10.210', # VM IP
    'localhost',
    '127.0.0.1'
]

CSRF_TRUSTED_ORIGINS = [
    'https://tobiasuihlein.de',
    'https://www.tobiasuihlein.de'
]

# Trust X-Forwarted-Proto header from reverse proxy after SSL termination
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# SSL termination is done by the proxy
SECURE_SSL_REDIRECT = False

# Session settings
SESSION_COOKIE_AGE = 86400  # 24 hours

# Static files settings
STATIC_ROOT = '/app/staticfiles'
STATIC_URL = 'static/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'