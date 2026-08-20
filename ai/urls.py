from django.urls import path

from . import views

app_name = 'ai'

urlpatterns = [
    path('', views.ai_index, name='index'),
    path('new/', views.ai_new, name='new'),
    path('<int:conv_id>/', views.ai_index, name='chat'),
    path('<int:conv_id>/send/', views.ai_send, name='send'),
    path('<int:conv_id>/send-ajax/', views.ai_send_ajax, name='send_ajax'),
    path('<int:conv_id>/delete/', views.ai_delete, name='delete'),
]
