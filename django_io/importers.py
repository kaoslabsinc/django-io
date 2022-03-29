import codecs
import csv
from collections import OrderedDict

from django.db import transaction
from django.forms.utils import ErrorDict


class DataImporterMeta(type):
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


class DataImporter(metaclass=DataImporterMeta):
    form_class = None

    @classmethod
    def check_extra_headers(cls, headers):
        return set(headers) - set(cls._label_to_keys_map.keys())

    @staticmethod
    def load_data_from_file(file):
        return csv.DictReader(codecs.iterdecode(file, 'utf-8-sig'))

    def translate_data(self, data):
        label_to_keys_map = self.__class__._label_to_keys_map
        return [
            {
                label_to_keys_map[label]: value
                for label, value in row.items()
                if label_to_keys_map.get(label)
            }
            for row in data
        ]

    def __init__(self, data):
        self.data = self.translate_data(data)
        self._errors = None
        self._forms = []

    def full_clean(self):
        self._errors = OrderedDict()
        for i, row in enumerate(self.data):
            form = self.form_class(row)
            self._forms.append(form)
            if not form.is_valid():
                self._errors[i] = form.errors

    @property
    def errors(self):
        if self._errors is None:
            self.full_clean()
        return self._errors

    @property
    def errors_formatted(self):
        keys_to_labels_map = self.__class__._keys_to_labels_map
        errors_formatted = OrderedDict()
        for i, error_row in self.errors.items():
            errors_formatted[i + 2] = ErrorDict(**{
                keys_to_labels_map[key]: errors
                for key, errors in error_row.items()
            })
        return errors_formatted

    def is_valid(self):
        return not self.errors

    def save(self):  # TODO: commit
        if self.errors:
            raise ValueError("Import could not be run because the data didn't validate")

        num_rows_written = 0
        with transaction.atomic():
            for form in self._forms:
                form.save()
                num_rows_written += 1
        return num_rows_written


__all__ = [
    'DataImporter',
]
