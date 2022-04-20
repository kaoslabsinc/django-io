from django.db import models


class ImportJobStatus(models.IntegerChoices):
    not_started = 0
    started = 20
    file_processed = 40
    file_errors = 41
    success = 100
    errors = 101


__all__ = [
    'ImportJobStatus',
]
