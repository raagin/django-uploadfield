from django.urls import path, include
from . import views

app_name = 'uploadfield'

# urls
urlpatterns = [
    path('upload/', views.upload_file, name='upload-file'),
    path('preview/', views.preview, name='preview-file'),
]