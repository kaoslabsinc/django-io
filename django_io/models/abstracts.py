import traceback

from django.core.files import File
from django.db import models, transaction
from django.utils.timezone import now
from django_fsm import FSMIntegerField, transition

from .enums import *


class DataImporter:
    file: File
    _clean_errors = dict

    def _file_to_unprocessed_data(self):
        raise NotImplementedError

    def full_clean(self, unprocessed_data):
        return unprocessed_data

    @property
    def clean_errors(self):
        if self._clean_errors is None:
            self.full_clean(self._file_to_unprocessed_data())
        return self._clean_errors

    def is_valid(self):
        return not self.clean_errors


class AbstractImportJob(models.Model):
    class Meta:
        abstract = True

    auto_start = True
    catch_exceptions = True

    file = models.FileField(upload_to='imports/')

    created_on = models.DateTimeField(auto_now_add=True)
    started_on = models.DateTimeField(null=True, blank=True)
    completed_on = models.DateTimeField(null=True, blank=True)
    status = FSMIntegerField(choices=ImportJobStatus.choices)

    errors = models.TextField(blank=True)

    @transition(status, source=(ImportJobStatus.not_started, ImportJobStatus.errors), target=ImportJobStatus.started)
    def start(self):
        self.started_on = now()

    @transition(status, source=ImportJobStatus.started, target=ImportJobStatus.success)
    def complete_successfully(self):
        self.completed_on = now()

    @transition(status, source=ImportJobStatus.started, target=ImportJobStatus.errors)
    def complete_w_errors(self, errors):
        self.completed_on = now()
        self.errors = errors

    def _process_file(self):
        raise NotImplementedError

    def _process_data(self, data):
        raise NotImplementedError

    def process(self):
        with transaction.atomic():
            self.start()
            self.save()
        try:
            data = self._process_file()
            self._process_data(data)
        except:
            with transaction.atomic():
                self.complete_w_errors(traceback.format_exc())
                self.save()
            if not self.catch_exceptions:
                raise
        else:
            with transaction.atomic():
                self.complete_successfully()
                self.save()

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super(AbstractImportJob, self).save(*args, **kwargs)

        if self.auto_start and self.status == ImportJobStatus.not_started:
            self.process()
