from django.db import models
from django_fsm import FSMIntegerField

from .enums import *


class AbstractJob(
    models.Model
):
    class Meta:
        abstract = True

    auto_start = True
    catch_exceptions = True

    created_on = models.DateTimeField(auto_now_add=True)
    started_on = models.DateTimeField(null=True, blank=True)
    completed_on = models.DateTimeField(null=True, blank=True)
    last_status_update = models.DateTimeField(null=True, blank=True)
    status = FSMIntegerField(choices=JobStatus.choices)

    errors = models.JSONField(null=True, blank=True)
    exceptions = models.TextField(blank=True)
