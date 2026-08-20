from django.urls import path

from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.forum_index, name='index'),
    path('category/<int:pk>/', views.forum_category, name='category'),
    path('category/<int:pk>/create/', views.forum_create_thread, name='create_thread'),
    path('thread/<int:pk>/', views.forum_thread, name='thread'),
    path('chat/', views.forum_chat, name='chat'),
    path('upload/', views.forum_upload, name='upload'),
]
