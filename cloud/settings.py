"""
Django settings for cloud project.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-ie5*rnrsw8_jn8afp60svp&h%eli-kkway(6_*$=387+cd!xec'

DEBUG = True

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'files',
    'office',
    'notes',
    'calendars',
    'forms',
    'forum',
    'contacts',
    'meet',
    'chat',
    'search',
    'mail',
    'tasks',
    'sites',
    'ai',
    'scheduler',
    'links',
    'dashboard',
    'payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cloud.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'calendars.context_processors.unread_notifications',
                'cloud.context_processors.sidebar',
            ],
        },
    },
]

WSGI_APPLICATION = 'cloud.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


LANGUAGE_CODE = 'az'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'files:index'
LOGOUT_REDIRECT_URL = 'landing'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# AI (CLX) assistant configuration
# Default: local Ollama. Set AI_PROVIDER='openai' to use an OpenAI-compatible API.
import os
AI_PROVIDER = os.environ.get('AI_PROVIDER', 'ollama')
AI_API_KEY = os.environ.get('AI_API_KEY', os.environ.get('ABACUS_API_KEY', ''))
AI_BASE_URL = os.environ.get('AI_BASE_URL', 'http://localhost:11434')
AI_MODEL = os.environ.get('AI_MODEL', 'dolphincoder:latest')

# Ko-fi payment integration
# KO_FI_USERNAME: your Ko-fi page username (e.g. 'altexel')
# KO_FI_VERIFICATION_TOKEN: the webhook verification token from Ko-fi settings
KO_FI_USERNAME = os.environ.get('KO_FI_USERNAME', 'altexel')
KO_FI_VERIFICATION_TOKEN = os.environ.get('KO_FI_VERIFICATION_TOKEN', '')
