from django.urls import path

from . import views

app_name = 'notes'

urlpatterns = [
    path('', views.notes_index, name='index'),
    path('create/', views.notes_create, name='create'),
    path('<int:pk>/', views.notes_edit, name='edit'),
    path('<int:pk>/delete/', views.notes_delete, name='delete'),
]
