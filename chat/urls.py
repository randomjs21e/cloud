from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_index, name='index'),
    path('create/', views.chat_create, name='create'),
    path('upload/', views.chat_upload, name='upload'),
    path('notifications-api/', views.chat_notifications_api, name='notifications_api'),
    path('private/<int:user_id>/', views.chat_private, name='private'),
    path('<int:pk>/', views.chat_room, name='room'),
    path('<int:pk>/delete/', views.chat_delete, name='delete'),
]
