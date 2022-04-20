from django.db import models
from django.utils.timezone import now
from django_fsm import FSMIntegerField, transition

from .enums import *


class AbstractImportJob(models.Model):
    class Meta:
        abstract = True
    
    auto_start = True

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

    def process_file(self):
        raise NotImplementedError

    def process_data(self, data):
        raise NotImplementedError

    def process(self):
        data = self.process_file()
        self.process_data(data)
