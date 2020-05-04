from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.template.defaultfilters import filesizeformat

from filebrowser.base import FileObject

from .conf import TEMP_DIR, THUMBNAIL
from .utils import handle_uploaded_file

@staff_member_required
def upload_file(request):
    if not request.is_ajax():
        raise PermissionDenied
    if request.method == 'POST' and request.FILES:
            f = request.FILES['files']
            tmp_file = handle_uploaded_file(f, to=TEMP_DIR)
            return JsonResponse({
                'success': True,
                'file': tmp_file
                })
    return JsonResponse({'success': False})
        
@staff_member_required
def preview(request):
    if not request.is_ajax():
        raise PermissionDenied

    file = request.GET.get('file')
    obj = FileObject(file) if file else ""
    print(obj.__dict__)
    return JsonResponse(dict(
        filename=obj.filename,
        url=obj.url,
        filetype=obj.filetype,
        filesize=filesizeformat(obj.filesize),
        thumbnail=obj.version_generate(THUMBNAIL).url if obj.filetype == 'Image' else None
    ))
        