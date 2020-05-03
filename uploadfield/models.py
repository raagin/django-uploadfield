import os
from django.db import models
from django.conf import settings

from filebrowser.base import FileObject

from uploadfield.conf import TEMP_DIR
from uploadfield.utils import check_existing, makedir, move_file, delete_file

class UploadFieldMixin:
    
    @classmethod
    def from_db(cls, db, field_names, values):
        _db = super().from_db(db, field_names, values)
        _db.__data = {}

        for f in field_names:
            value = getattr(_db, f)
            field_cls = cls._meta.get_field(f)
            if field_cls.__class__.__name__ == 'UploadField':
                _db.__data[f] = dict(initial_value=str(value))
        return _db

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)        
        if hasattr(self, '_UploadFieldMixin__data'):
            for attname, obj in self._UploadFieldMixin__data.items():
                
                initial_value = obj['initial_value']
                value = obj.get('value', None)
                value_path = value.path if value else ""
                directory = obj.get('directory', None)

                if initial_value == value_path:
                    continue
                
                # if value changed
                # value can be empty or not
                if value and value_path.startswith(TEMP_DIR):
                    # move file from temporary folder to main storage
                    # and set instance attr new file path
                    # 1. find directory
                    if directory:
                        if callable(directory):
                            new_path = directory(self)
                        else:    
                            new_path = directory.format(id=self.id)
                        if not new_path.endswith('/'):
                            new_path += '/'
                    else:
                        new_path = ""
                    # 2. make new path
                    new_file_path = value_path.replace(TEMP_DIR, new_path)
                    new_file_path = check_existing(new_file_path)
                    
                    # 3. make dir if not exists
                    makedir(os.path.dirname(
                            os.path.join(settings.MEDIA_ROOT, new_file_path)))
                    
                    # 4. delete tmp version
                    value.delete_versions()
                    # 5. move
                    move_file(value_path, new_file_path)

                    # set new path to instance. we can't use self because of inlines
                    # also can be in the list
                    setattr(self, attname, FileObject(new_file_path))

                # value is empty and initial_value not empty
                # delete file if field cleared or changed
                if initial_value:
                    delete_file(FileObject(initial_value))

            # we delete this key because will call 'save' again
            del self._UploadFieldMixin__data
            self.save()