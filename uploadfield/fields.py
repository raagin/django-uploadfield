import os
import json
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.db.models.fields import CharField
from django.templatetags.static import static
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
from django.conf import settings

from filebrowser.fields import FileBrowseWidget, FileBrowseFormField
from filebrowser.base import FileObject
from filebrowser.sites import site
from filebrowser.settings import VERSIONS

from .conf import THUMBNAIL, KEEP_FILES_ON_DELETE, BASE_URL, DZ_DEFAULT_OPTIONS

class UploadFieldWidget(FileBrowseWidget):
    template_name = 'uploadfield/uploadfield_widget.html'

    def __init__(self, attrs={}):
        super().__init__(attrs)
        self.site = attrs.get('filebrowser_site', None)
        self.extensions = attrs.get('extensions', '')
        self.dropzone_options = DZ_DEFAULT_OPTIONS
        self.dropzone_options.update(attrs.get('dropzone_options', {}))
        self.base_url = attrs.get('base_url')
        self.static_folder = attrs.get('static_folder')
        self.thumbnail = attrs.get('thumbnail', '')
        if attrs is not None:
            self.attrs = attrs.copy()
        else:
            self.attrs = {}
        super().__init__(attrs)

    class Media:
        css = {
            'all': (
                static('uploadfield/vendor/jquery.fancybox.min.css'),
                static('uploadfield/css/uploadfield.css'),
                )
        }
        js = (
            static('uploadfield/vendor/vue.min.js'),
            static('uploadfield/vendor/jquery.fancybox.min.js'),
            static('uploadfield/vendor/dropzone/dropzone.js'),
            static('uploadfield/vendor/js.cookie.js'),
            static('uploadfield/js/uploadfield.js'),
            )

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ""
        if value != "" and not isinstance(value, FileObject):
            value = FileObject(value, site=self.site)
        final_attrs = self.build_attrs(attrs, extra_attrs={"type": self.input_type, "name": name})
        final_attrs['data-extensions'] = json.dumps(self.extensions)
        final_attrs['data-dropzone-options'] = json.dumps(self.dropzone_options)
        final_attrs['data-base-url'] = self.base_url
        final_attrs['data-static-folder'] = self.static_folder
        final_attrs['data-thumbnail_size'] = "{}"
        if self.thumbnail:
            final_attrs['data-thumbnail'] = self.thumbnail

        fb_version = VERSIONS.get(self.thumbnail, None)
        if fb_version:
            final_attrs['data-thumbnail_size'] = json.dumps(dict(
                width=fb_version['width'],
                height=fb_version['height']
                ))
        
        filebrowser_site = self.site
        allowed_title = _('Allowed')
        return render_to_string("uploadfield/uploadfield_widget.html", locals())


class UploadField(CharField):
    description = "UploadField"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 255
        self.site = kwargs.pop('filebrowser_site', site)
        self.directory = kwargs.pop('directory', '')
        self.extensions = kwargs.pop('extensions', [])
        self.dropzone_options = kwargs.pop('dropzone_options', {})
        self.method = kwargs.pop('method', None)
        self.rename = kwargs.pop('rename', None)
        self.base_url = kwargs.pop('base_url', BASE_URL)
        self.keep_files_on_delete = kwargs.pop('keep_files_on_delete', KEEP_FILES_ON_DELETE)
        self.thumbnail = kwargs.pop('thumbnail', '')
        return super().__init__(*args, **kwargs)
        

    def clean(self, value, model_instance):
        value = super().clean(value, model_instance)
        obj = {
            'value': value,
            'directory': self.directory,
            'method': self.method,
            'rename': self.rename,
            'keep_files_on_delete': self.keep_files_on_delete
        }
        if not hasattr(model_instance, '_UploadFieldMixin__data'):
            # add instance
            obj['initial_value'] = ""
            v = {}
            v[self.attname] = obj
            setattr(model_instance, '_UploadFieldMixin__data', v)
        elif self.attname in model_instance._UploadFieldMixin__data:
            # change instance
            model_instance._UploadFieldMixin__data[self.attname].update(obj)
        else:
            model_instance._UploadFieldMixin__data[self.attname] = obj
        return value

    def to_python(self, value):
        if not value or isinstance(value, FileObject):
            return value
        return FileObject(value, site=self.site)

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def get_prep_value(self, value):
        if not value or not isinstance(value, FileObject):
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
        attrs["thumbnail"] = self.thumbnail
        attrs["dropzone_options"] = self.dropzone_options
        attrs["base_url"] = self.base_url
        attrs["static_folder"] = settings.STATIC_URL
        defaults = {
            'widget': widget_class(attrs=attrs),
            'form_class': FileBrowseFormField,
            'filebrowser_site': self.site,
            'directory': self.directory,
            'extensions': self.extensions
        }
        return super().formfield(**defaults)


FORMFIELD_FOR_DBFIELD_DEFAULTS[UploadField] = {'widget': UploadFieldWidget}
