import os
from pathlib import Path

import dotenv
import geopy

dotenv.load_dotenv()
import logging

import dj_database_url
import django_heroku
import redis
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

SITE_ID = 3

# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "social_django",
    "rest_framework",
    "drf_yasg",
    "users",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "resume",
    "company",
    "dashboard",
    "job",
    "website",
    "widget_tweaks",
    "crispy_forms",
    "crispy_bootstrap5",
    "geopy",
    "onboarding",
    "django_filters",
    # 'easyaudit',
    "asseessments",
    "social_features",
    "messaging",
    "notifications",
    "channels",
    "cities_light",
    "django_ckeditor_5",
    "videochat",
    "paypal.standard.ipn",
    "transactions",
    "corsheaders",
]


ASGI_APPLICATION = "umemployed.asgi.application"

SITE_URL = os.getenv("SITE_URL", "http://localhost:8000")
# REDIS_URL  = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1')

# settings.py
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GENAI_API_KEY")
LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")


import logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

import os
import ssl
import urllib.parse

from channels_redis.core import RedisChannelLayer

# Load environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


# Ensure ssl_cert_reqs is set for rediss:// URLs for Celery
def add_ssl_cert_reqs(url):
    if url.startswith("rediss://") and "ssl_cert_reqs" not in url:
        if "?" in url:
            return url + "&ssl_cert_reqs=CERT_NONE"
        else:
            return url + "?ssl_cert_reqs=CERT_NONE"
    return url


CELERY_BROKER_URL = add_ssl_cert_reqs(REDIS_URL)
CELERY_RESULT_BACKEND = add_ssl_cert_reqs(REDIS_URL)

# Channels configuration
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}

# Caching setup using Redis
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 10,  # in seconds
            "SOCKET_TIMEOUT": 10,
            "CONNECTION_POOL_CLASS_KWARGS": {
                "ssl": False,  # Disable SSL
            },
        },
    }
}

# Celery configuration
accept_content = ["application/json"]
result_serializer = "json"
task_serializer = "json"

# Celery task discovery
CELERY_IMPORTS = [
    "resume.tasks",
    "job.tasks",
    "users.tasks",
    "messaging.tasks",
]

CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_ALLOWED_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "easyaudit.middleware.easyaudit.EasyAuditMiddleware",  # Moved after auth
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "users.middleware.EmailVerificationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "umemployed.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                "social_django.context_processors.backends",
                "users.context_processors.add_company_to_context",  # Add this line
            ],
        },
    },
]

WSGI_APPLICATION = "umemployed.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# DATABASES = {
#     'default': dj_database_url.config(
#         default=os.getenv('DATABASE_URL'),
#         conn_max_age=0,  # 0 seconds (0 minutes) for connection reuse
#     )
# }

# DATABASES = {
#     'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("AZURE_DB_NAME"),
        "USER": os.getenv("AZURE_DB_USER"),
        "PASSWORD": os.getenv(
            "AZURE_DB_PASSWORD",
        ),
        "HOST": os.getenv(
            "AZURE_DB_HOST",
        ),
        "PORT": os.getenv(
            "AZURE_DB_PORT",
        ),
        "OPTIONS": {
            "sslmode": "require",
        },
    }
}

ADMINS = [("Nyuydine Bill", "billleynyuy@gmail.com")]
MANAGERS = ADMINS


# Automatically send a confirmation email after signup
ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # options: "none", "optional", "mandatory"
ACCOUNT_EMAIL_REQUIRED = True

# Only allow login if the email is verified
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3

ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = "switch_account"  # If user is logged in
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = "switch_account"

LOGIN_URL = "/accounts/user/login"
LOGOUT_URL = "logout"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT = "/"

SOCIAL_AUTH_GOOGLE_OAUTH_KEY = os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH_SECRET = os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH_SECRET")
SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI")
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = SOCIAL_AUTH_GOOGLE_OAUTH_KEY  # This is the same as above
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = SOCIAL_AUTH_GOOGLE_OAUTH_SECRET  # This is the same as above

LOGIN_REDIRECT_URL = "/"  # URL to redirect to after login

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar.events",
]

# Additional Google OAuth2 settings
SOCIAL_AUTH_GOOGLE_OAUTH2_USE_DEPRECATED_API = False
SOCIAL_AUTH_GOOGLE_OAUTH2_IGNORE_DEFAULT_SCOPE = True
SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {'access_type': 'offline', 'approval_prompt': 'force'}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True


CSRF_TRUSTED_ORIGINS = [
    "https://umemployed-f6fdddfffmhjhjcj.canadacentral-01.azurewebsites.net",
    "https://umemployed.azurewebsites.net",
    "http://localhost:8000",  # Add local backend
    "http://127.0.0.1:8000",  # Add alternative local backend
    "https://umemployed-front-end.vercel.app",  # Add frontend
]
SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "users.pipeline.associate_by_email",  # Include the custom function here
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
)

ACCOUNT_EMAIL_REQUIRED = True  # new
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"  # new
EMAIL_HOST = "smtp.gmail.com"  # new
EMAIL_PORT = 587  # new
EMAIL_HOST_USER = "info@umemployed.com"  # new
EMAIL_HOST_PASSWORD = "hszd wpet pnre asce"  # new
EMAIL_USE_TLS = True  # new
DEFAULT_FROM_EMAIL = "info@umemployed.com"


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Ensure timezone-aware datetime objects
import django.utils.timezone
django.utils.timezone.activate('UTC')

# Azure Blob Storage settings
AZURE_ACCOUNT_NAME = config("AZURE_ACCOUNT_NAME")
AZURE_ACCOUNT_KEY = config("AZURE_ACCOUNT_KEY")
AZURE_CONTAINER = config("AZURE_CONTAINER")
AZURE_CUSTOM_DOMAIN = f"{AZURE_ACCOUNT_NAME}.blob.core.windows.net"

# Media files settings
MEDIA_URL = f"https://{AZURE_CUSTOM_DOMAIN}/{AZURE_CONTAINER}/"
DEFAULT_FILE_STORAGE = "storages.backends.azure_storage.AzureStorage"

# Static files settings
STATIC_URL = f"https://{AZURE_CUSTOM_DOMAIN}/{AZURE_CONTAINER}/"
STATICFILES_STORAGE = "storages.backends.azure_storage.AzureStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = ["users.backend.EmailBackend"]

# Local static files settings (if needed for development)
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"  # Update the path to an absolute path


AUTHENTICATION_BACKENDS = [
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
]

OPENAI_API_KEY = config("OPENAI_API_KEY")
SECRET_KEY = config("SECRET_KEY")
GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET")
PAYPAL_RECEIVER_EMAIL = "business@umemployed.com"
PAYPAL_TEST = True  # Set to False for live transactions


# Stripe API Keys
STRIPE_LIVE_MODE = True
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="your-default-stripe-secret-key")
STRIPE_PUBLISHABLE_KEY = config(
    "STRIPE_PUBLISHABLE_KEY", default="your-default-stripe-publishable-key"
)
STRIPE_WEBHOOK_SECRET = config(
    "STRIPE_WEBHOOK_SECRET", default="your-default-stripe-webhook-secret"
)

django_heroku.settings(locals())
# CKEditor settings
customColorPalette = [
    {"color": "hsl(4, 90%, 58%)", "label": "Red"},
    {"color": "hsl(340, 82%, 52%)", "label": "Pink"},
    {"color": "hsl(291, 64%, 42%)", "label": "Purple"},
    {"color": "hsl(262, 52%, 47%)", "label": "Deep Purple"},
    {"color": "hsl(231, 48%, 48%)", "label": "Indigo"},
    {"color": "hsl(207, 90%, 54%)", "label": "Blue"},
]
CKEDITOR_UPLOAD_PATH = "uploads/"

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": {
            "items": [
                "heading",
                "|",
                "bold",
                "italic",
                "link",
                "bulletedList",
                "numberedList",
                "blockQuote",
                "imageUpload",
            ],
        }
    },
    "extends": {
        "blockToolbar": [
            "paragraph",
            "heading1",
            "heading2",
            "heading3",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote",
        ],
        "toolbar": {
            "items": [
                "heading",
                "|",
                "outdent",
                "indent",
                "|",
                "bold",
                "italic",
                "link",
                "underline",
                "strikethrough",
                "code",
                "subscript",
                "superscript",
                "highlight",
                "|",
                "codeBlock",
                "sourceEditing",
                "insertImage",
                "bulletedList",
                "numberedList",
                "todoList",
                "|",
                "blockQuote",
                "imageUpload",
                "|",
                "fontSize",
                "fontFamily",
                "fontColor",
                "fontBackgroundColor",
                "mediaEmbed",
                "removeFormat",
                "insertTable",
            ],
            "shouldNotGroupWhenFull": True,
        },
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "imageStyle:alignCenter",
                "imageStyle:side",
                "|",
            ],
            "styles": [
                "full",
                "side",
                "alignLeft",
                "alignRight",
                "alignCenter",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ],
            "tableProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
            "tableCellProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
        },
        "heading": {
            "options": [
                {"model": "paragraph", "title": "Paragraph", "class": "ck-heading_paragraph"},
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
            ]
        },
    },
    "list": {
        "properties": {
            "styles": True,
            "startIndex": True,
            "reversed": True,
        }
    },
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",  # Change this to AllowAny
    ),
}

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=200000),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {"Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}},
    "USE_SESSION_AUTH": False,
    "JSON_EDITOR": True,
}

# Frontend URL for OAuth redirects
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

# CORS configuration
CORS_ALLOW_CREDENTIALS = True  # Allow cookies to be included in cross-origin requests
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000", 
    "https://umemployed-front-end.vercel.app",
    "http://127.0.0.1:3000",  # Add this for local development
    "https://umemployed-f6fdddfffmhjhjcj.canadacentral-01.azurewebsites.net",  # Azure backend
    "https://accounts.google.com",  # Allow Google OAuth
]

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Store sessions in database
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = True  # Save session on every request
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Don't expire when browser closes
SESSION_COOKIE_SECURE = True  # Use secure cookies in production
SESSION_COOKIE_HTTPONLY = False  # Must be False for cross-origin OAuth
SESSION_COOKIE_SAMESITE = 'None'  # Allow cross-origin requests
SESSION_COOKIE_NAME = 'umemployed_sessionid'  # Custom name to avoid conflicts
