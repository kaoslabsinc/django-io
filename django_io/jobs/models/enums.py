from django.db import models


class JobStatus(models.IntegerChoices):
    not_started = 0
    queued = 1
    started = 10
    error = 99
    done = 100


__all__ = [
    'JobStatus',
]
