# -*- coding: utf-8 -*-

DEFAULT_TIMEZONE = 'UTC'
DEBUG = False
PROFILE = False
SECRET_KEY = 'ReplaceItWithSecretString'
SESSION_PREFIX = 'gaesess:'
COOKIE_AGE = 1209600
COOKIE_NAME = 'KAY_SESSION'

ADMINS = (
)

TEMPLATE_DIRS = (
)

USE_I18N = False
DEFAULT_LANG = 'en'

MIDDLEWARE_CLASSES = (
    'kay.auth.middleware.AuthenticationMiddleware',
    'kay.sessions.middleware.SessionMiddleware',
    'kay.utils.flash.FlashMiddleware',
)

INSTALLED_APPS = (
    'kay.auth',
    'core',
    'main',
    'admin',
)

APP_MOUNT_POINTS = {
    'main': '/',
    'admin': '/admin',
}

AUTH_USER_MODEL = 'core.models.AdminUser'

# You can remove following settings if unnecessary.
CONTEXT_PROCESSORS = (
    'kay.context_processors.request',
    'kay.context_processors.url_functions',
    'kay.context_processors.media_url',
)
