from django.urls import path

from . import views

app_name = 'office'

urlpatterns = [
    path('', views.office_index, name='index'),
    path('create/', views.office_create, name='create'),
    path('open-file/<int:file_pk>/', views.office_open_file, name='open_file'),
    path('<int:pk>/', views.office_edit, name='edit'),
    path('<int:pk>/delete/', views.office_delete, name='delete'),
    path('<int:pk>/export/', views.office_export, name='export'),
]
