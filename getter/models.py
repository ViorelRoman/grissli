from __future__ import unicode_literals

from django.db import models

# Create your models here.
class URLs(models.Model):
    url = models.CharField(max_length=1024)
    timeshift = models.TimeField(blank=True, null=True)

    def __unicode__(self):
        return self.url

    class Meta:
        verbose_name = 'URLs'
        verbose_name_plural = 'URLs'


class URLInfo(models.Model):
    url = models.ForeignKey(URLs)
    title = models.TextField(blank=True)
    charset = models.CharField(max_length=128, blank=True)
    h1 = models.TextField(blank=True)
    parsed_date = models.DateTimeField()
    status = models.BooleanField(default=True)

    def __unicode__(self):
        return self.url.url

    class Meta:
        verbose_name = 'URLInfo'
        verbose_name_plural = 'URLInfo'
