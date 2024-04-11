import logging

from django.conf import settings

if settings.DEBUG:
    log = logging.getLogger("debug")
else:
    log = logging.getLogger("default")
