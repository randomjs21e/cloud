from django.urls import path

from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.tasks_index, name='index'),
    path('list/<int:list_id>/', views.tasks_index, name='list'),
    path('list/create/', views.task_list_create, name='list_create'),
    path('list/<int:pk>/delete/', views.task_list_delete, name='list_delete'),
    path('list/<int:list_id>/task/create/', views.task_create, name='task_create'),
    path('task/<int:pk>/toggle/', views.task_toggle, name='task_toggle'),
    path('task/<int:pk>/delete/', views.task_delete, name='task_delete'),
]
