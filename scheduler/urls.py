from django.urls import path

from . import views

app_name = 'scheduler'

urlpatterns = [
    path('', views.scheduler_index, name='index'),
    path('create/', views.scheduler_create, name='create'),
    path('<int:pk>/delete/', views.scheduler_delete, name='delete'),
    path('<int:pk>/bookings/', views.scheduler_bookings, name='bookings'),
    path('s/<slug:slug>/', views.scheduler_public, name='public'),
]
