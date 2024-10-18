from pathlib import Path
import os
import geopy
import dotenv
dotenv.load_dotenv()
from decouple import config
import dj_database_url  
import django_heroku
import redis
import logging



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

SITE_ID = 3

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'social_django',

    'users',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'resume', 
    'company',
    'dashboard',
    'job',
    'website',
    'widget_tweaks',
    'crispy_forms',
    'crispy_bootstrap5',
    'geopy',
    'onboarding',
    'django_filters',
    # 'easyaudit',
    'asseessments',
    'social_features',
    'messaging',
    'notifications',
    
    'channels',
    'cities_light',
    
    'ckeditor',
    'ckeditor_uploader',
]

ASGI_APPLICATION = 'umemployed.asgi.application'

REDIS_URL  = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1')

import logging
from channels_redis.core import RedisChannelLayer

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],  # Ensure Redis is running here
        },
    },
}
# Caching setup using Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'ssl_cert_reqs': None,  # This allows self-signed certificates
            },
        },
    }
}

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL



CRISPY_TEMPLATE_PACK = 'bootstrap5'
CRISPY_ALLOWED_TEMPLATE_PACK='bootstrap5'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'easyaudit.middleware.easyaudit.EasyAuditMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    # 'umemployed.middleware.RedirectBasedOnRoleMiddleware',

     # Add the account middleware:
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'umemployed.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'social_django.context_processors.backends',
                'users.context_processors.add_company_to_context',  # Add this line
            ],
        },
    },
]

WSGI_APPLICATION = 'umemployed.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
  
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'd97r55prv16las',
        'USER': 'u3mlos1b16lhnu',
        'PASSWORD': 'p5d239049119450812c414a246b1be69bc8479bb870fc89fca6bcdbc1f082f3c5',
        'HOST': 'c9pv5s2sq0i76o.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com',  
        'PORT': '5432',      
    }
}

# DATABASES = {  
#     'default': {  
#         'ENGINE': 'django.db.backends.sqlite3',  
#         'NAME': BASE_DIR / "db.sqlite3",  
#     }  
# }

ADMINS = [('Nyuydine Bill', 'billleynyuy@gmail.com')]
MANAGERS = ADMINS


# Automatically send a confirmation email after signup
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # options: "none", "optional", "mandatory"
ACCOUNT_EMAIL_REQUIRED = True

# Only allow login if the email is verified
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True  
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3

ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = 'switch_account'  # If user is logged in
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = 'switch_account' 

LOGIN_URL='/accounts/user/login'
LOGOUT_URL='logout'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT='/'

SOCIAL_AUTH_GOOGLE_OAUTH_KEY = '38566500036-s92j092h19cnf0seht935oatlm9bb67a.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH_SECRET = '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'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = SOCIAL_AUTH_GOOGLE_OAUTH_KEY  # This is the same as above
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = SOCIAL_AUTH_GOOGLE_OAUTH_SECRET  # This is the same as above

LOGIN_REDIRECT_URL = '/'  # URL to redirect to after login

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]

CSRF_TRUSTED_ORIGINS = ['https://umemployed-app-afec951f7ec7.herokuapp.com', 'http://127.0.0.1:8000', 'https://umemployed-development-8475c5e1c4b7.herokuapp.com',]

SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = 'https://umemployed-app-afec951f7ec7.herokuapp.com/social-auth/complete/google-oauth2/'

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'users.pipeline.associate_by_email',  # Include the custom function here
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

ACCOUNT_EMAIL_REQUIRED = True #new
ACCOUNT_LOGOUT_REDIRECT_URL='/'

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' #new
# EMAIL_HOST = 'smtp.gmail.com' #new
# EMAIL_PORT = 587 #new
# EMAIL_HOST_USER = 'billleynyuy@gmail.com'  #new
# EMAIL_HOST_PASSWORD = "hlvr rkdd irly osnl" #new
# EMAIL_USE_TLS = True #new
# DEFAULT_FROM_EMAIL = 'billleynyuy@gmail.com'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' #new
EMAIL_HOST = 'mail.umemployed.com' #new
EMAIL_PORT = 465 #new
EMAIL_HOST_USER = 'info@umemployed.com'  #new
EMAIL_HOST_PASSWORD = "guew cfro yuao tkiz" #new
EMAIL_USE_TLS = True #new
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Azure Blob Storage settings
AZURE_ACCOUNT_NAME = config('AZURE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = config('AZURE_ACCOUNT_KEY')
AZURE_CONTAINER = config('AZURE_CONTAINER')
AZURE_CUSTOM_DOMAIN = f'{AZURE_ACCOUNT_NAME}.blob.core.windows.net'

# Media files settings
MEDIA_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_CONTAINER}/'
DEFAULT_FILE_STORAGE = "storages.backends.azure_storage.AzureStorage"

# Static files settings
STATIC_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_CONTAINER}/'
STATICFILES_STORAGE = "storages.backends.azure_storage.AzureStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = ['users.backend.EmailBackend']

# Local static files settings (if needed for development)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Update the path to an absolute path

# CKEditor settings
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'width': '100%',
        'height': 300,
    },
}

AUTHENTICATION_BACKENDS = [
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

OPENAI_API_KEY = config('OPENAI_API_KEY')
SECRET_KEY = config('SECRET_KEY')
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET')

django_heroku.settings(locals())