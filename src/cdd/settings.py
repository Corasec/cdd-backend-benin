"""
Django settings for cdd project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os
import environ
from django.utils.translation import gettext_lazy as _

try:
    from .local_settings import *  # noqa: F403
except ImportError:
    from .local_settings_template import *  # noqa: F403

    print("No local_settings.py, used .local_settings_template")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# https://django-environ.readthedocs.io/en/latest/
env = environ.Env()
env.read_env()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", False)

ALLOWED_HOSTS = env("ALLOWED_HOSTS", list, ["localhost"])


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

CREATED_APPS = [
    "authentication",
    "dashboard",
    "attachments",
    "process_manager",
    "administrativelevels",
]

THIRD_PARTY_APPS = [
    "bootstrap4",
    "drf_spectacular",
    "rest_framework",
]

INSTALLED_APPS += CREATED_APPS + THIRD_PARTY_APPS + LOCAL_INSTALLED_APPS

MIDDLEWARE = LOCAL_MIDDLEWARE + [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # tries to determine user's language using URL language prefix
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cdd.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "dashboard.context_processors.settings_vars",  # Called the function which presents the globals variables
            ],
        },
    },
]

WSGI_APPLICATION = "cdd.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

EXTERNAL_DATABASE_NAME = "mis"

DATABASES = {"default": env.db()}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

USE_L10N = True

# Translation
LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

LANGUAGES = [
    ("en", _("English")),
    ("fr", _("French")),
]

# Format localization
# https://docs.djangoproject.com/en/4.0/topics/i18n/formatting/#format-localization

DATE_INPUT_FORMATS = [
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%d/%m/%y",  # '25-10-2006', '25/10/2006', '25/10/06'
    "%d %b %Y",
    "%d %b, %Y",  # '25 Oct 2006', '25 Oct, 2006'
    "%d %B %Y",
    "%d %B, %Y",  # '25 October 2006', '25 October, 2006'
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR / "dashboard/static",
]

MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB


MEDIA_ROOT = BASE_DIR / "media/"

MEDIA_URL = "/media/"


MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/"

LOGIN_REDIRECT_URL = "dashboard:facilitators:list"

LOGOUT_REDIRECT_URL = "/"


# CouchDB

NO_SQL_USER = env("NO_SQL_USER")

NO_SQL_PASS = env("NO_SQL_PASS")

NO_SQL_URL = env("NO_SQL_URL")


REST_FRAMEWORK = {
    # https://github.com/tfranzel/drf-spectacular
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


# S3
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_STORAGE_BUCKET_NAME = env("S3_BUCKET")

AWS_ACCESS_KEY_ID = env("S3_ACCESS")

AWS_SECRET_ACCESS_KEY = env("S3_SECRET")


# Mapbox
MAPBOX_ACCESS_TOKEN = env("MAPBOX_ACCESS_TOKEN")

DIAGNOSTIC_MAP_LATITUDE = env("DIAGNOSTIC_MAP_LATITUDE")

DIAGNOSTIC_MAP_LONGITUDE = env("DIAGNOSTIC_MAP_LONGITUDE")

DIAGNOSTIC_MAP_ZOOM = env("DIAGNOSTIC_MAP_ZOOM")

DIAGNOSTIC_MAP_WS_BOUND = env("DIAGNOSTIC_MAP_WS_BOUND")

DIAGNOSTIC_MAP_EN_BOUND = env("DIAGNOSTIC_MAP_EN_BOUND")

DIAGNOSTIC_MAP_ISO_CODE = env("DIAGNOSTIC_MAP_ISO_CODE")


# Global variables
OTHER_LANGUAGES = True
