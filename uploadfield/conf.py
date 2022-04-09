from django.conf import settings

TEMP_DIR = getattr(settings, "UPLOADFIELD_TEMP_DIR", 'tmp/')
THUMBNAIL = getattr(settings, "UPLOADFIELD_THUMBNAIL", 'admin_thumbnail')
KEEP_FILES_ON_DELETE = getattr(settings, "UPLOADFIELD_KEEP_FILES_ON_DELETE", False)
