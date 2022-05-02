from django import forms

__all__ = [
    'CurrencyField',
    'PercentageField',
    'ListField',
    'FormattedIntegerField',
]


class CurrencyField(forms.DecimalField):
    def to_python(self, value):
        value = str(value).strip()
        value = value.replace(',', '').lstrip('$')
        return super(CurrencyField, self).to_python(value)


class PercentageField(forms.DecimalField):
    def to_python(self, value):
        if value in self.empty_values:
            return None
        value = str(value).strip()
        if value[-1] == '%':
            value = super(PercentageField, self).to_python(value[:-1]) / 100
        else:
            value = super(PercentageField, self).to_python(value)
        return value


class ListField(forms.CharField):
    def __init__(self, seperator=',', *args, **kwargs):
        self.seperator = seperator
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        value = super(ListField, self).to_python(value)
        return [item.strip() for item in value.split(self.seperator)]


class FormattedIntegerField(forms.IntegerField):
    def to_python(self, value):
        value = value.replace(',', '')
        return super(FormattedIntegerField, self).to_python(value)
