"""
Django settings for TwoMove project.
Configurado para uso con MySQL, autenticación personalizada por correo y envío de correos electrónicos (verificación de usuario).
"""

from pathlib import Path
import os

# ========================
# 🔧 CONFIGURACIÓN BÁSICA
# ========================

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-*@tu+vrjbu2*s(=7)b7c^6oj#@yt0si6!!ontd5#w%1*&hv3_+'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']  # Agrega tu dominio al desplegar

# ========================
# 🧩 APLICACIONES
# ========================

INSTALLED_APPS = [
    # Django apps base
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps internas
    'apps.users',
    'apps.bikes',
    'apps.stations',
    'apps.rentals',

    # Librerías externas
    'rest_framework',
]

# ========================
# ⚙️ MIDDLEWARE
# ========================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'TwoMove.urls'

# ========================
# 🎨 TEMPLATES
# ========================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Carpeta global opcional
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

WSGI_APPLICATION = 'TwoMove.wsgi.application'

# ========================
# 🛢️ BASE DE DATOS (MySQL)
# ========================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'twomovedb',             # ← Nombre de tu base de datos
        'USER': 'root',                   # ← Usuario MySQL
        'PASSWORD': 'sHA*1028480099',     # ← Contraseña MySQL
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ========================
# 🔒 VALIDACIÓN DE CONTRASEÑAS
# ========================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========================
# 🌍 INTERNACIONALIZACIÓN
# ========================

LANGUAGE_CODE = 'es-co'      # Español Colombia
TIME_ZONE = 'America/Bogota' # Zona horaria local
USE_I18N = True
USE_TZ = True

# ========================
# 📁 ARCHIVOS ESTÁTICOS Y MEDIA
# ========================

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ========================
# 📧 CONFIGURACIÓN DE CORREO (verificación usuario)
# ========================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'twomoveee@gmail.com'
EMAIL_HOST_PASSWORD = 'wtac dfvx jhtd ycwu'   # Contraseña de aplicación
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Durante desarrollo, puedes usar esta opción si no quieres enviar correos reales:
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ========================
# ⚙️ CONFIGURACIONES ADICIONALES
# ========================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========================
# 🔐 AUTENTICACIÓN PERSONALIZADA
# ========================

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'users.Usuario'

# Backend de autenticación (permite login por correo)
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = 'users:login'

# ========================
# 🧰 REST FRAMEWORK
# ========================

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}

# ========================
# ✅ LOGGING BÁSICO
# ========================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
