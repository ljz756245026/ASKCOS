"""
Django settings for askcos_site project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = os.path.dirname(__file__)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'px$*ir)-wd=x6^!r++t53ik^2)z7!9cvw+m#@!-$ut@xjyjtg*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

TEMPLATE_LOADERS = ['django.template.loaders.filesystem.Loader',
 'django.template.loaders.app_directories.Loader']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_PATH, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'askcos_site.main',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'askcos_site.urls'

WSGI_APPLICATION = 'askcos_site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
# AUTHENTICATION_BACKENDS = (
#     'mongoengine.django.auth.MongoEngineBackend',
# )

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_ROOT = os.path.join(PROJECT_PATH, 'static/')
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',    
) 
STATICFILES_DIRS = (
    os.path.join(STATIC_ROOT, 'css'),
    os.path.join(STATIC_ROOT, 'js')
    )

# Media files
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media/')
MEDIA_URL = '/media/'

# Miscellanious
RETRO_TRANSFORMS = {
    'database': 'reaxys',
    'collection': 'transforms_retro_v4', # 'lowe' or 'chematica'
    'mincount': 1500,
}
RETRO_TRANSFORMER = {
    'parallel': True,
    'nb_workers': 2,
}
SYNTH_TRANSFORMS = {
    'database': 'reaxys',
    'collection': 'transforms_forward_v1',
    'mincount': 500, 
}
SYNTH_TRANSFORMER = {
}
INSTANCES = {
    'database': 'reaxys',
    'collection': 'instances',
}
REACTIONS = {
    'database': 'reaxys',
    'collection': 'reactions',
}
CHEMICALS = {
    'database': 'reaxys',
    'collection': 'chemicals',
}
BUYABLES = {
    'database': 'reaxys',
    'collection': 'buyables',
}
SOLVENTS = {
    'database': 'reaxys',
    'collection': 'solvents',
}

PREDICTOR = {
    'nb_workers': 2,
    'trained_model_path': '/home/ccoley/ML Chemistry/Make-It/makeit/predict/output/01_23_2017',
    'info': '01-23-17, model trained on 80k Reaxys examples, validated on 10k, tested on 10k. Nh1_200, Nh2_200, Nh3_200, l2_0, Nc_5000, enh_weight_0d1, context_weight_50, opt_adadelta, batch_5, moreFeatures'
}

CONTEXT_REC = {
    'info_path': os.path.join(PROJECT_PATH, 'testModel', '1650000-1699999_10NN_20000SRR_info.txt'),
    'model_path': os.path.join(PROJECT_PATH, 'testModel', '1650000-1699999_10NN_20000SRR_lshf.pickle'),
}

# LOGIN
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'
