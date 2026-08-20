from django.urls import path

from . import views

app_name = 'search'

urlpatterns = [
    path('', views.search_index, name='index'),
    path('ai/', views.search_ai_ajax, name='ai'),
]
