import os

from config.django.base import *  # noqa

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("PROD_DB_NAME"),
        "USER": os.getenv("PROD_DB_USER"),
        "PASSWORD": os.getenv("PROD_DB_PASSWORD"),
        "HOST": os.getenv("PROD_DB_HOST"),
        "PORT": os.getenv("PROD_DB_PORT"),
    }
}
