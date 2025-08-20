from .settings import *  # import base settings

DEBUG = False

ALLOWED_HOSTS = ["*", "127.0.0.1", "localhost"] # or restrict to API Gateway + domain later

# Any overrides specific to prod
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")