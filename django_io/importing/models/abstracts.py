import traceback

from django.db import models, transaction
from django.db.models.base import ModelBase
from django.utils.timezone import now
from django_fsm import FSMIntegerField, transition

from .enums import *
from .mixins import *


class AbstractImportJob(
    RawDataValidatorMixin,
    DataProcessorMixin,
    models.Model
):
    class Meta:
        abstract = True

    auto_start = True
    catch_exceptions = True

    file = models.FileField(upload_to='imports/')

    created_on = models.DateTimeField(auto_now_add=True)
    started_on = models.DateTimeField(null=True, blank=True)
    completed_on = models.DateTimeField(null=True, blank=True)
    last_status_update = models.DateTimeField(null=True, blank=True)
    status = FSMIntegerField(choices=ImportJobStatus.choices)

    data = models.JSONField(null=True, blank=True)

    errors = models.JSONField(null=True, blank=True)
    exceptions = models.TextField(blank=True)

    @transition(
        status,
        source=(ImportJobStatus.not_started,
                ImportJobStatus.file_processed,
                ImportJobStatus.file_errors,
                ImportJobStatus.errors),
        target=ImportJobStatus.started
    )
    def start(self):
        self.last_status_update = self.started_on = now()

    @transition(status, source=ImportJobStatus.started, target=ImportJobStatus.file_processed)
    def mark_file_processed(self):
        self.last_status_update = now()

    @transition(status, source=ImportJobStatus.started, target=ImportJobStatus.file_errors)
    def mark_file_errors(self, errors):
        self.last_status_update = now()
        self.errors = errors

    @transition(status, source=ImportJobStatus.file_processed, target=ImportJobStatus.success)
    def mark_success(self):
        self.last_status_update = self.completed_on = now()

    @transition(status, target=ImportJobStatus.errors)
    def mark_errors(self, formatted_stacktrace):
        self.last_status_update = now()
        self.exceptions = formatted_stacktrace

    def is_valid(self):
        pass

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


class SheetImporterMeta(ModelBase):
    """Collect Fields declared on the base classes."""

    @property
    def _label_to_keys_map(cls):
        return {
            field.label or key: key
            for key, field in cls.form_class.base_fields.items()
        }

    @property
    def _keys_to_labels_map(cls):
        return {
            key: field.label or key
            for key, field in cls.form_class.base_fields.items()
        }


class AbstractSheetImportJob(AbstractImportJob, metaclass=SheetImporterMeta):
    class Meta:
        abstract = True

    form_class = None

    def _process_file(self):
        pass

    def _process_data(self, data):
        pass

    def get_instances(self):
        return [form.get_instance() for form in self._forms]

    def save_data(self):
        if self.errors:
            raise ValueError("Import could not be run because the data didn't validate")

        self.model.objects.bulk_update_or_create(self.get_instances())
