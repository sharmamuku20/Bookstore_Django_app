# settings_prod.py

from pathlib import Path
import os
from datetime import timedelta
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Helper function to get environment variables.
def get_env_var(var_name, default=None):
    """
    Retrieves an environment variable. If not found, returns a default value
    or raises an error if no default is provided.
    """
    value = os.getenv(var_name)
    if value is None and default is None:
        raise ImproperlyConfigured(f"Environment variable '{var_name}' is required for configuration.")
    return value if value is not None else default

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_var('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_env_var('DEBUG', 'False').lower() in ['true', '1', 'yes']

ALLOWED_HOSTS = get_env_var(
    "ALLOWED_HOSTS",
    "*"
).split(",")

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',
    'django_filters',
    'django_extensions',
    'drf_yasg',
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

ROOT_URLCONF = 'bookstore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'bookstore.wsgi.application'

# Production Database settings for AWS RDS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_env_var('POSTGRES_DB'),
        'USER': get_env_var('POSTGRES_USER'),
        'PASSWORD': get_env_var('POSTGRES_PASSWORD'),
        'HOST': get_env_var('POSTGRES_HOST'),
        'PORT': get_env_var('POSTGRES_PORT'),
        'OPTIONS': {
            'sslmode': os.getenv("POSTGRES_SSLMODE", "require")
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# DRF settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# Production-specific security settings
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Add this at the end of your settings_prod.py file

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
        }
    },
    'USE_SESSION_AUTH': False,
    'VALIDATOR_URL': None,
    # This is the critical line to load static files from a CDN
    'DEFAULT_AUTO_SCHEMA_CLASS': 'drf_yasg.inspectors.SwaggerAutoSchema',
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch',
        'head',
        'options',
    ],
    'ENABLED_FOR_METHODS': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    'DEFAULT_GENERATOR_SCHEMA_CLASS': 'drf_yasg.generators.OpenAPISchemaGenerator',
    'PUBLIC_SETTINGS': {
        'use_authentication': False,
        'use_session_auth': False,
    },
    'USE_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch',
        'head',
        'options',
    ],
    'SPEC_URL_CONF': 'bookstore.urls',
    'DEFAULTS': {
        'ui': {
            'show_endpoints': True,
        },
    },
    'DOC_EXPANSION': 'none',
    'OPERATIONS_SORTER': 'alpha',
    'TAGS_SORTER': 'alpha',
    'PERSIST_AUTHORIZATION': True,
    'BASE_URL': None,
    'DEFAULT_MODEL_RENDERING': 'example',
    'DEFAULT_INFO_HEADER': {
        'title': 'Bookstore API',
        'description': 'API for a bookstore application',
    },
    'SERVE_INCLUDE_SCHEMA_URL': False,
    'JSON_SCHEMA_API_VERSION': '3.0.0',
    'JSON_SCHEMA_DEFAULT_VERSION': '3.0.0',
    'JSON_SCHEMA_3': {
        'DEFAULT_TAGS': [],
    },
    'SECURITY_REQUIREMENTS': [],
    'STATIC_URL': '[https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.25.0/](https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.25.0/)',
}
