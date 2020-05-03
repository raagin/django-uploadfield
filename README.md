# Django Uploadfield
Direct uploading files and handling it in templates with [Django FileBrowser](https://github.com/sehmaschine/django-filebrowser/) (FB).

Feeatures:
- Dropdown
- Dynamic preview and file info
- Static or dynamic destination folder

django-uploadfield uses Dropzone.js, Vue, jQuery and Fancybox js modules. \
Project in development stage. Now it works only in django admin interface.

In plans:
- Custom file and image processing function.
- Make it work outside of Django admin and with DjangoRestFramework.

## Installation

```bash
pip install git+https://github.com/raagin/django-uploadfield.git
```

## Requirements
Same as for https://github.com/sehmaschine/django-filebrowser/

## How to use

**1. Add modules to INSTALLED_APPS**

```python
INSTALLED_APPS = [
    ...
    'uploadfield',
    'filebrowser',
    ...
    ]
```

**2. Add module urls**
```python
# urls.py
urlpatterns = [
    ...
    path('uploadfield/', include('uploadfield.urls'))
]
```

**3. In models.py**
```python
# models.py
from django.db import models

from uploadfield.fields import UploadField
from uploadfield.models import UploadFieldMixin

class MyModel(UploadFieldMixin, models.Model):
    image = UploadField(
        directory='myimages/',
        extensions=[".jpg", "png"]
        )
    file = UploadField(
        directory=lambda o: f'myfiles/{o.id}/'
        )
```
Field have same options with FileBrowserField
- `directory` option of FB is overrided and can be callable or string.
- `extensions` are optional.
- Use `blank=True` for the possibility of an empty value

**4. In templates**
It is the same as for django-filebrowser
Read more: https://django-filebrowser.readthedocs.io/en/latest/

## Settings
You may reasign this default values:
```python
UPLOADFIELD_TEMP_DIR = 'tmp/'
UPLOADFIELD_THUMBNAIL = 'admin_thumbnail'
```
