from django.contrib import admin


class DataImportableAdmin(admin.ModelAdmin):
    change_list_template = 'django_io/admin/change_list.html'
    upload_url = None

    def get_upload_url(self):
        return self.upload_url

    def changelist_view(self, request, extra_context=None):
        extra_context = {
            'upload_url': self.get_upload_url(),
            **(extra_context or {}),
        }
        return super(DataImportableAdmin, self).changelist_view(request, extra_context)


__all__ = [
    'DataImportableAdmin',
]
