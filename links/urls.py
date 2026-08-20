from django.urls import path

from . import views

app_name = 'links'

urlpatterns = [
    path('', views.links_index, name='index'),
    path('create/', views.links_create, name='create'),
    path('<int:pk>/delete/', views.links_delete, name='delete'),
    path('r/<str:code>/', views.links_redirect, name='redirect'),
]
