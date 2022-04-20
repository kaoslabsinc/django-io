from typing import Union


class RawDataValidatorMixin:
    raw_data = Union[dict, list]
    cleaned_data = Union[dict, list]
    _clean_errors = Union[dict, list]

    def full_clean(self):
        self.cleaned_data = self.raw_data

    @property
    def clean_errors(self):
        if self._clean_errors is None:
            self.full_clean()
        return self._clean_errors

    def is_valid(self):
        return not self.clean_errors


class DataProcessorMixin:
    cleaned_data = Union[dict, list]
    _processing_errors = Union[dict, list]

    def process_data(self):
        raise NotImplementedError


__all__ = [
    'RawDataValidatorMixin',
    'DataProcessorMixin',
]
