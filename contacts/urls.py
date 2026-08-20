from django.urls import path

from . import views

app_name = 'contacts'

urlpatterns = [
    path('', views.contacts_index, name='index'),
    path('create/', views.contacts_create, name='create'),
    path('<int:pk>/edit/', views.contacts_edit, name='edit'),
    path('<int:pk>/delete/', views.contacts_delete, name='delete'),
    path('suggest/<int:user_id>/', views.contacts_add_suggestion, name='add_suggestion'),
]
