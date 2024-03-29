"""
Django settings for StockManager project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import StockManager.subSettings as CONFI
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
#BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#ROOT_DIR = os.path.dirname(BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = CONFI.DJANGO_SECRET

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = False
DEBUG = CONFI.DEBUG

ALLOWED_HOSTS = ['hjyang.iptime.org',
                 'localhost',
                 # Data
                 'http://data.krx.co.kr/',
                 '*',
                 'django', # proxy for nginx
                 'http://stockmanager.site',
                 'stockmanager.site'
                 ]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_apscheduler',
    'corsheaders',
    'rest_framework', # DRF를 앱으로 등록
    'rest_framework_swagger',
    'rest_framework.authtoken',
    'log_viewer', # Viewer for logs
    'bootstrap4',
    'rangefilter',
    #'tailwind', 'theme',

    # my apps
    'appStockInfo',
    'appRestAPI',
    'appStockPrediction',
    'appStockAccount'
]

# Custom user model
AUTH_USER_MODEL = 'appStockAccount.User'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'whitenoise.middleware.WhiteNoiseMiddleware'

]

ROOT_URLCONF = 'StockManager.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
                    # BASE_DIR / 'templates'
                    os.path.join(BASE_DIR, 'templates'),
                    #
                    # os.path.join(BASE_DIR, 'templates'),
                    # os.path.join(BASE_DIR, 'staticfiles' , 'templates'),
                    # os.path.join(BASE_DIR, 'static' , 'templates'),
        ],
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

WSGI_APPLICATION = 'StockManager.wsgi.application'


# Rest API framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', #1
        'NAME': 'stockmanager', #2
        'USER': CONFI.DB_USERNAME, #3
        'PASSWORD': CONFI.DB_PASSWORD,  #4
        'HOST': 'hjyang.iptime.org',   #5
        'PORT': '44441', #6
        'TEST': {
                    'NAME': 'myteststockmanager',
                },
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ORIGIN_WHITELIST = [
                         'http://127.0.0.1:5552',
                         'http://localhost:5552',
                         'http://hjyang.iptime.org',
                         'http://hjyang.iptime.org:4441',
                         'http://stockmanager.site',
                         # Data
                         'http://data.krx.co.kr',
                         ]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'PATCH',
    'POST',
    'PUT'
]
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
    'referer'
]

# App scheduler settings
APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"
SCHEDULER_DEFAULT = True

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/
# https://query.tistory.com/entry/Dj-%EC%9E%A5%EA%B3%A0-%EB%8B%A4%EA%B5%AD%EC%96%B4-%EC%A7%80%EC%9B%90-%EC%82%AC%EC%9A%A9%EB%B2%95-i18n
LANGUAGE_CODE = 'ko'
LANGUAGES = [        # 사용하고자 하는 언어를 모두 적어줍니다.
    ('ko', 'Korean'),
    ('en-us', 'English'),
]
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]



TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ =  False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
# https://listed.to/@toolate/6967/heroku-x-django-static
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
if CONFI.DEBUG == True:
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static'),
        #os.path.join(BASE_DIR, 'staticfiles'),
    ]
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    #STATIC_ROOT = os.path.join(BASE_DIR, 'static')
else:
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static'),
        os.path.join(BASE_DIR, 'staticfiles'),
    ]
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    #STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


## logging config
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        },
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s \n'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'INFO',
            'encoding': 'utf-8',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/mysite.log'),
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'appStockInfo': {
            'level': 'INFO',
            'encoding': 'utf-8',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/appStockInfo.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'appStockPrediction': {
            'level': 'INFO',
            'encoding': 'utf-8',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/appStockPrediction.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins', 'file'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'my': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'appStockInfo': {
            'handlers': ['console', 'appStockInfo'],
            'level': 'INFO',
        },
        'appStockPrediction': {
            'handlers': ['console', 'appStockPrediction'],
            'level': 'INFO',
        },
    }
}
LOG_VIEWER_FILES = ['mysite']
LOG_VIEWER_FILES_PATTERN = '*.log'
LOG_VIEWER_FILES_DIR = os.path.join(BASE_DIR, 'logs/')
#-------------
LOG_VIEWER_PAGE_LENGTH = 25       # total log lines per-page
LOG_VIEWER_MAX_READ_LINES = 1000  # total log lines will be read
LOG_VIEWER_PATTERNS = ['[INFO]', '[DEBUG]', '[WARNING]', '[ERROR]', '[CRITICAL]']


# Django test configuration
# https://github.com/realpython/django-slow-tests
TEST_RUNNER = 'django_slowtests.testrunner.DiscoverSlowestTestsRunner'
NUM_SLOW_TESTS = None # generate full tests reports
# (Optional)
SLOW_TEST_THRESHOLD_MS = 2000  # Only show tests slower than 200ms
# (Optional)
ALWAYS_GENERATE_SLOW_REPORT = True  # Generate report only when requested using --slowreport flag