from django.urls import path

from . import views

app_name = 'mail'

urlpatterns = [
    path('', views.mail_index, name='index'),
    path('inbox/', views.mail_inbox, name='inbox'),
    path('sent/', views.mail_sent, name='sent'),
    path('starred/', views.mail_starred, name='starred'),
    path('archived/', views.mail_archived, name='archived'),
    path('trash/', views.mail_trash, name='trash'),
    path('compose/', views.mail_compose, name='compose'),
    path('<int:pk>/', views.mail_detail, name='detail'),
    path('<int:pk>/action/', views.mail_action, name='action'),
]
