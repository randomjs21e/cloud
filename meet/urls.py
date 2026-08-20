from django.urls import path

from . import views

app_name = 'meet'

urlpatterns = [
    path('', views.meet_index, name='index'),
    path('create/', views.meet_create, name='create'),
    path('<int:pk>/', views.meet_join, name='join'),
    path('<int:pk>/delete/', views.meet_delete, name='delete'),
]
