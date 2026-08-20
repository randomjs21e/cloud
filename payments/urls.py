from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.plan_view, name='plan'),
    path('ko-fi-webhook/', views.ko_fi_webhook, name='ko_fi_webhook'),
]
