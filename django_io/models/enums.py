from django.db import models


class ImportJobStatus(models.IntegerChoices):
    not_started = 0
    started = 20
    success = 100
    errors = 101


__all__ = [
    'ImportJobStatus',
]
