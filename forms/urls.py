from django.urls import path

from . import views

app_name = 'forms'

urlpatterns = [
    path('', views.forms_index, name='index'),
    path('create/', views.forms_create, name='create'),
    path('<int:pk>/', views.forms_edit, name='edit'),
    path('<int:pk>/delete/', views.forms_delete, name='delete'),
    path('<int:pk>/responses/', views.forms_responses, name='responses'),
    path('f/<str:token>/', views.forms_fill, name='fill'),
    path('f/<str:token>/thanks/', views.forms_thanks, name='thanks'),
]
