# Django I/O

Importing and exporting of data, and other file operations for Django apps

## Quick start

```shell
pip install django-io
```

Add `django_io` to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    ...,
    'django_io',
]
```

Create a form to upload your data and save it, and the view to show the form. In the admin panel for the model you are
importing:

```python
@admin.register(SomeModel)
class SomeModelAdmin(
    DataImportableAdmin,
    admin.ModelAdmin
):
    upload_url = reverse_lazy('app:model:upload')  # path to the view
```

## Development and Testing

### IDE Setup

Add the `example` directory to the `PYTHONPATH` in your IDE to avoid seeing import warnings in the `tests` modules. If
you are using PyCharm, this is already set up.

### Running the Tests

Install requirements

```
pip install -r requirements.txt
```

For local environment

```
pytest
```

For all supported environments

```
tox
```
