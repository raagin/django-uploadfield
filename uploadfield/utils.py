import os
from uuid import uuid4

from django.conf import settings
from django.core.files.storage import DefaultStorage

from filebrowser.utils import convert_filename

storage = DefaultStorage()

def move_file(temp_path, file_path):
    storage.move(temp_path, file_path)

def check_existing(file_path):
    if os.path.exists(file_path):
        # add hash to file name if same name exists
        file_basename, file_ext = os.path.splitext(file_path)
        file_path = "%s_%s%s" % (file_basename, uuid4().hex[:7], file_ext)
    file_name = os.path.basename(file_path)
    print(file_name)
    return (file_path, file_name)

def makedir(dir_path):
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
        except FileExistsError:
            pass

def handle_uploaded_file(f, to):
    file_name = convert_filename(str(f))
    to_dir = os.path.join(settings.MEDIA_ROOT, *to.split('/'))
    
    makedir(to_dir)
    
    file_path = os.path.join(to_dir, file_name)
    file_path, file_name = check_existing(file_path)
    
    with open(file_path, 'wb+') as image_file:
        for chunk in f.chunks():
            image_file.write(chunk)

    file_url = to + file_name
    return file_url

def delete_file(file):
    if file:
        file.delete()
        file.delete_versions()