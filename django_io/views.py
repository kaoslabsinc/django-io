from django import forms
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import FormView


class UploadDataForm(forms.Form):
    sheet = forms.FileField()


class DataImportView(SuccessMessageMixin, FormView):
    form_class = UploadDataForm
    template_name = 'django_io/upload_data.html'
    success_message = "Successfully imported {n} {verbose_name_plural}"

    importer_class = None
    success_url = None
    item_verbose_name = 'item'
    item_verbose_name_plural = None
    sample_sheet = None
    back_url = None

    def __init__(self, *args, **kwargs):
        super(DataImportView, self).__init__(*args, **kwargs)
        self.num_rows_written = None

    def get_item_verbose_name_plural(self):
        return self.item_verbose_name_plural or self.item_verbose_name + 's'

    def get_back_url(self):
        return self.back_url

    def data_invalid(self, importer):
        return self.render_to_response(self.get_context_data(errors=importer.errors_formatted))

    def form_valid(self, form):
        data = self.importer_class.load_data_from_file(form.files['sheet'])
        importer = self.importer_class(data)
        if importer.is_valid():
            self.num_rows_written = importer.save()
        else:
            return self.data_invalid(importer)

        return super(DataImportView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(DataImportView, self).get_context_data(**kwargs)
        return {
            **context,
            'sample_sheet': self.sample_sheet,
            'verbose_name': self.item_verbose_name,
            'verbose_name_plural': self.get_item_verbose_name_plural(),
            'back_url': self.get_back_url(),
        }

    def get_success_message(self, cleaned_data):
        return self.success_message.format(n=self.num_rows_written,
                                           verbose_name_plural=self.get_item_verbose_name_plural())


__all__ = [
    'DataImportView',
]
