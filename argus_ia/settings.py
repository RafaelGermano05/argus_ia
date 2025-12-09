"""
Django settings for argus_ia project.
"""

import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ====================
# SECURITY
# ====================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-argus-ia-2024')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Railway environment detection
IS_RAILWAY = os.environ.get('RAILWAY_ENVIRONMENT') is not None
IS_PRODUCTION = not DEBUG or IS_RAILWAY

# ====================
# HOSTS & DOMAINS
# ====================

# Default allowed hosts
default_hosts = ['localhost', '127.0.0.1', '.railway.app']

# Add Railway public domain if available
railway_host = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
if railway_host:
    default_hosts.append(railway_host)

# Custom hosts from environment
custom_hosts = os.environ.get('ALLOWED_HOSTS', '').split(',')
custom_hosts = [h.strip() for h in custom_hosts if h.strip()]

# Combine all allowed hosts
ALLOWED_HOSTS = list(set(default_hosts + custom_hosts))

# ====================
# APPLICATION DEFINITION
# ====================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'detection',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Deve vir depois de SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'argus_ia.urls'

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

WSGI_APPLICATION = 'argus_ia.wsgi.application'

# ====================
# DATABASE
# ====================

# Database configuration with Railway priority
if 'DATABASE_URL' in os.environ:
    # Railway PostgreSQL
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True
        )
    }
elif IS_RAILWAY and not DEBUG:
    # Railway production without DATABASE_URL (fallback)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('PGDATABASE', 'railway'),
            'USER': os.environ.get('PGUSER', 'postgres'),
            'PASSWORD': os.environ.get('PGPASSWORD', ''),
            'HOST': os.environ.get('PGHOST', 'localhost'),
            'PORT': os.environ.get('PGPORT', '5432'),
        }
    }
else:
    # Development SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ====================
# PASSWORD VALIDATION
# ====================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ====================
# INTERNATIONALIZATION
# ====================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# ====================
# STATIC FILES (WhiteNoise)
# ====================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Static files directories
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Storage backend for WhiteNoise
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_ALLOW_ALL_ORIGINS = True

# ====================
# SESSION & COOKIES
# ====================

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600  # 1 hora
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ====================
# SECURITY SETTINGS
# ====================

# CSRF Settings
CSRF_TRUSTED_ORIGINS = []

# Add Railway domains to CSRF trusted origins
if IS_RAILWAY:
    CSRF_TRUSTED_ORIGINS.append('https://*.railway.app')
    if railway_host:
        CSRF_TRUSTED_ORIGINS.append(f'https://{railway_host}')

# Add custom trusted origins from environment
custom_csrf_origins = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if custom_csrf_origins:
    origins = [o.strip() for o in custom_csrf_origins.split(',') if o.strip()]
    CSRF_TRUSTED_ORIGINS.extend(origins)

# Security settings for production
if IS_PRODUCTION:
    # SSL/HTTPS settings
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Cookie security
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    
    # HTTP Strict Transport Security
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Other security headers
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Referrer policy
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    
    # Content Security Policy (opcional, pode ajustar conforme necessidade)
    # SECURE_CSP = "default-src 'self'"
    
    # Para Railway, é importante essa configuração:
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True

# ====================
# LOGGING
# ====================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# ====================
# OTHER SETTINGS
# ====================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Port configuration for Railway
PORT = int(os.environ.get('PORT', 8000))

# File upload settings
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Maximum size for file uploads (10MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

# Email settings (para produção)
if IS_PRODUCTION:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    # Configure suas credenciais de email aqui se necessário
    # EMAIL_HOST = os.environ.get('EMAIL_HOST')
    # EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
    # EMAIL_USE_TLS = True
    # EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    # EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache settings (simples para começar)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Para desenvolvimento local, desabilite algumas medidas de segurança
if DEBUG and not IS_RAILWAY:
    # Desabilita SSL redirect em desenvolvimento
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    
    # Mostra SQL queries no console (útil para debug)
    LOGGING['loggers']['django.db.backends'] = {
        'level': 'DEBUG',
        'handlers': ['console'],
    }