
from pathlib import Path
import os
import geopy
import dotenv
dotenv.load_dotenv()
import dj_database_url  
import django_heroku


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ALLOWED_HOSTS = ['*']

SITE_ID = 2


# Application definition

INSTALLED_APPS = [
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

]
ASGI_APPLICATION = 'umemployed.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

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
  
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'd6i1ltsqgns6s',
        'USER': 'u7v7567lb4cv3v',
        'PASSWORD': 'pa5b0269bb80a7b8539744a189b01892c03ccbf806328c2faa2b8d39d408398f9',
        'HOST': 'cd1goc44htrmfn.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com',  
        'PORT': '5432',      
    }
}

# DATABASES = {
#     'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
# }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}


# Automatically send a confirmation email after signup
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # options: "none", "optional", "mandatory"
ACCOUNT_EMAIL_REQUIRED = True

# Only allow login if the email is verified
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True  

ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = 'switch_account'  # If user is logged in
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = 'switch_account' 



# SOCIALACCOUNT_PROVIDERS = {
#     'google': {
#         'SCOPE': ['profile', 'email'],
#         'AUTH_PARAMS': {'access_type': 'online'},
#         'OAUTH_PKCE_ENABLED': True,
#         'APP': {
#             'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
#             'secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
#             'key': ''
#         }
#     }
# }

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

# For local development
SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = 'http://localhost:8000/social-auth/complete/google-oauth2/'

# For production
SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI_PROD = 'https://umemployed-web-63d4d135b077.herokuapp.com/social-auth/complete/google-oauth2/'
import os

if os.getenv('DJANGO_ENV') == 'production':
    SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI_PROD
else:
    SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = 'http://localhost:8000/social-auth/complete/google-oauth2/'


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
ACCOUNT_EMAIL_VERIFICATION = 'none'



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' #new
EMAIL_HOST = 'smtp.gmail.com' #new
EMAIL_PORT = 587 #new
EMAIL_HOST_USER = 'billleynyuy@gmail.com'  #new
EMAIL_HOST_PASSWORD = "hlvr rkdd irly osnl" #new
EMAIL_USE_TLS = True #new
DEFAULT_FROM_EMAIL = 'billleynyuy@gmail.com'




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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS =['users.backend.EmailBackend']

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Update the path to an absolute path

#media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# AUTHENTICATION_BACKENDS = (
    
#     # Needed to login by username in Django admin, regardless of `allauth`
#     'django.contrib.auth.backends.ModelBackend',

#     # `allauth` specific authentication methods, such as login by email
#     'allauth.account.auth_backends.AuthenticationBackend'
# )

AUTHENTICATION_BACKENDS = [
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

from decouple import config

OPENAI_API_KEY = config('OPENAI_API_KEY')
SECRET_KEY = config('SECRET_KEY')
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET')
DJANGO_ENV = config('DJANGO_ENV', default='development')

django_heroku.settings(locals())

