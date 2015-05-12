#!/usr/bin/env python
# coding: utf-8

from django.db import models


class IgnoredUrls(models.Model):
    url = models.CharField(
        verbose_name=u"Ignored url pattern", default='^/', max_length=12800)

    class Meta:
        verbose_name = u"ignored url pattern"
        verbose_name_plural = u"ignored url patterns"

    def __unicode__(self):
        return self.url


class MaintenanceMode(models.Model):
    enable_maintenance_mode = models.BooleanField(
        verbose_name=u"Enable maintenance mode?", default=False)
    allow_superuser = models.BooleanField(
        verbose_name=u"Allow superuser to enter site?", default=True)
    ignored_urls = models.ManyToManyField(IgnoredUrls, blank=True)

    class Meta:
        verbose_name = u"maintenance mode"
        verbose_name_plural = u"maintenance modes"

    def __unicode__(self):
        return u"%s maintenance mode, superuser access %s, %s urls ignored" % \
            ("Enabled" if self.enable_maintenance_mode else "Disabled",
             "allowed" if self.allow_superuser else "disallowed",
             self.ignored_urls.count())
