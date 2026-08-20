from django.urls import path

from . import views

app_name = 'files'

urlpatterns = [
    path('', views.file_index, name='index'),
    path('folder/<int:folder_id>/', views.file_index, name='folder'),
    path('folder/create/', views.folder_create, name='folder_create'),
    path('folder/<int:pk>/delete/', views.folder_delete, name='folder_delete'),
    path('upload/', views.file_upload, name='upload'),
    path('photos/', views.photos_index, name='photos'),
    path('photos/upload/', views.photos_upload, name='photos_upload'),
    path('albums/create/', views.album_create, name='album_create'),
    path('albums/<int:pk>/', views.album_detail, name='album'),
    path('albums/<int:pk>/add/', views.album_add_photo, name='album_add'),
    path('albums/<int:pk>/remove/<int:file_id>/', views.album_remove_photo, name='album_remove'),
    path('albums/<int:pk>/delete/', views.album_delete, name='album_delete'),
    path('drives/', views.drive_index, name='drives'),
    path('drives/create/', views.drive_create, name='drive_create'),
    path('drives/<int:pk>/', views.drive_detail, name='drive'),
    path('drives/<int:pk>/add-member/', views.drive_add_member, name='drive_add_member'),
    path('drives/<int:pk>/remove-member/<int:user_id>/', views.drive_remove_member, name='drive_remove_member'),
    path('drives/<int:pk>/upload/', views.drive_upload, name='drive_upload'),
    path('drives/<int:pk>/download/<int:file_id>/', views.drive_download, name='drive_download'),
    path('drives/<int:pk>/delete-file/<int:file_id>/', views.drive_delete_file, name='drive_delete_file'),
    path('drives/<int:pk>/delete/', views.drive_delete, name='drive_delete'),
    path('trash/', views.file_trash_list, name='trash'),
    path('<int:pk>/download/', views.file_download, name='download'),
    path('<int:pk>/delete/', views.file_delete, name='delete'),
    path('<int:pk>/trash/', views.file_trash, name='trash_file'),
    path('<int:pk>/restore/', views.file_restore, name='restore'),
    path('<int:pk>/move/', views.file_move, name='move'),
    path('<int:pk>/share/', views.file_set_share, name='share'),
    path('<int:pk>/versions/', views.file_versions, name='versions'),
    path('<int:pk>/versions/upload/', views.file_version_upload, name='version_upload'),
    path('<int:pk>/versions/<int:version_id>/download/', views.file_version_download, name='version_download'),
    path('s/<str:token>/', views.file_public, name='public'),
    path('s/<str:token>/download/', views.file_public_download, name='public_download'),
]
