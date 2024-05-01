import os
from .base import *
DEBUG = False
ADMINS = [
    ('leekeunha','leetoya@naver.com'),
]
ALLOWED_HOSTS=['http://healthdiary.com','https://healthdiary.com','healthdiary.com','www.healthdiary.com']

DATABASES = {
    'default':{
        'ENGINE':'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST':'db',
        'PORT':5432,
    }
}

REDIS_URL = 'redis://cache:6379'
CACHES['default']['LOCATION'] = REDIS_URL
CHANNEL_LAYERS['default']['CONFIG']['hosts'] = [REDIS_URL]
