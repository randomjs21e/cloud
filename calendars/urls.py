from django.urls import path

from . import views

app_name = 'calendars'

urlpatterns = [
    path('', views.calendars_index, name='index'),
    path('create/', views.calendars_create, name='create'),
    path('<int:pk>/', views.calendars_detail, name='detail'),
    path('<int:pk>/edit/', views.calendars_edit, name='edit'),
    path('<int:pk>/delete/', views.calendars_delete, name='delete'),
    path('invitation/<int:pk>/', views.invitation_respond, name='invitation_respond'),
    path('notifications/', views.notifications_index, name='notifications'),
]
