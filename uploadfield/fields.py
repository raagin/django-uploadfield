import os
import json
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.db.models.fields import CharField
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS

from filebrowser.fields import FileBrowseWidget, FileBrowseFormField
from filebrowser.base import FileObject
from filebrowser.sites import site

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


class UploadField(CharField):
    description = "UploadField"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 255
        self.site = kwargs.pop('filebrowser_site', site)
        self.directory = kwargs.pop('directory', '')
        self.extensions = kwargs.pop('extensions', '')
        self.method = kwargs.pop('method', None)
        return super().__init__(*args, **kwargs)
        

    def clean(self, value, model_instance):
        value = super().clean(value, model_instance)
        obj = {
            'value': value,
            'directory': self.directory,
            'method': self.method
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

    def to_python(self, value):
        if not value or isinstance(value, FileObject):
            return value
        return FileObject(value, site=self.site)

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def get_prep_value(self, value):
        if not value:
            return value
        return value.path

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        if not value:
            return value
        if type(value) is str:
            return value
        return value.path

    def formfield(self, **kwargs):
        widget_class = kwargs.get('widget', UploadFieldWidget)
        attrs = {}
        attrs["filebrowser_site"] = self.site
        attrs["directory"] = self.directory
        attrs["extensions"] = self.extensions
        defaults = {
            'widget': widget_class(attrs=attrs),
            'form_class': FileBrowseFormField,
            'filebrowser_site': self.site,
            'directory': self.directory,
            'extensions': self.extensions
        }
        return super().formfield(**defaults)


FORMFIELD_FOR_DBFIELD_DEFAULTS[UploadField] = {'widget': UploadFieldWidget}
