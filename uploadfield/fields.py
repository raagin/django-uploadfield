import os
import json
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS

from filebrowser.fields import FileBrowseField, FileBrowseWidget
from filebrowser.base import FileObject

from .conf import THUMBNAIL

class UploadFieldWidget(FileBrowseWidget):
    template_name = 'uploadfield/uploadfield_widget.html'

    class Media:
        css = {
            'all': (
                '/static/uploadfield/vendor/jquery.fancybox.min.css',
                '/static/uploadfield/css/uploadfield.css',
                )
        }
        js = (
            '/static/uploadfield/vendor/vue.min.js',
            '/static/uploadfield/vendor/jquery.fancybox.min.js',
            '/static/uploadfield/vendor/dropzone/dropzone.js',
            '/static/uploadfield/vendor/js.cookie.js',
            '/static/uploadfield/js/uploadfield.js',
            )

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ""
        if value != "" and not isinstance(value, FileObject):
            value = FileObject(value, site=self.site)
        final_attrs = self.build_attrs(attrs, extra_attrs={"type": self.input_type, "name": name})
        final_attrs['extensions'] = json.dumps(self.extensions)
        allowed_title = _('Allowed')
        return render_to_string("uploadfield/uploadfield_widget.html", locals())


class UploadField(FileBrowseField):
    description = "UploadField"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 255
        super().__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        value = super().clean(value, model_instance)
        obj = {
            'value': value,
            'directory': self.directory
        }
        if not hasattr(model_instance, '_UploadFieldMixin__data'):
            # add instance
            obj['initial_value'] = ""
            v = {}
            v[self.attname] = obj
            setattr(model_instance, '_UploadFieldMixin__data', v)
        else:
            # change instance
            model_instance._UploadFieldMixin__data[self.attname].update(obj)
        return value


FORMFIELD_FOR_DBFIELD_DEFAULTS[UploadField] = {'widget': UploadFieldWidget}
