#!/usr/bin/env python
# coding: utf-8

import re

import django
from django.conf import settings
from django.core import urlresolvers

from .models import MaintenanceMode


if django.VERSION[:2] <= (1, 3):
    from django.conf.urls import defaults as urls
else:
    from django.conf import urls

from maintenancemode.conf.settings.defaults import (
    MAINTENANCE_MODE, MAINTENANCE_IGNORE_URLS)

urls.handler503 = 'maintenancemode.views.defaults.temporary_unavailable'
urls.__all__.append('handler503')

IGNORE_URLS = [re.compile(url) for url in MAINTENANCE_IGNORE_URLS]


class MaintenanceModeMiddleware(object):
    def process_request(self, request):
        # Allow access if middleware is not activated
        enabled_maintenance_modes = \
            MaintenanceMode.objects.filter(enable_maintenance_mode=True)
        enabled_maintenance_mode = \
            enabled_maintenance_modes[0] if enabled_maintenance_modes else None
        if not MAINTENANCE_MODE and not enabled_maintenance_mode:
            return None

        # Allow access if remote ip is in INTERNAL_IPS
        if request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
            return None

        # Allow access if the user doing the request is logged in and a
        # superuser.
        superuser_from_model_enabled = enabled_maintenance_mode.allow_superuser
        ALLOW_SU = getattr(settings, 'MAINTENANCE_ALLOW_SU', False)
        if (
                (ALLOW_SU or superuser_from_model_enabled) and
                hasattr(request, 'user') and
                request.user.is_superuser
        ):
            return None

        # update list of ignored urls with ignored url from model
        for ignore_url in enabled_maintenance_mode.ignored_urls.all():
            IGNORE_URLS.append(re.compile(ignore_url.url))

        # Check if a path is explicitly excluded from maintenance mode
        for url in IGNORE_URLS:
            if url.match(request.path_info):
                return None

        # Otherwise show the user the 503 page
        resolver = urlresolvers.get_resolver(None)

        callback, param_dict = resolver.resolve_error_handler('503')
        return callback(request, **param_dict)
