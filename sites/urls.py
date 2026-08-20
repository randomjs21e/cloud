from django.urls import path

from . import views

app_name = 'sites'

urlpatterns = [
    path('', views.sites_index, name='index'),
    path('create/', views.sites_create, name='create'),
    path('<slug:slug>/', views.site_public, name='public'),
    path('<slug:slug>/admin/', views.sites_dashboard, name='dashboard'),
    path('<slug:slug>/admin/edit/', views.sites_edit, name='edit'),
    path('<slug:slug>/admin/delete/', views.sites_delete, name='delete'),
    path('<slug:slug>/admin/post/new/', views.post_create, name='post_create'),
    path('<slug:slug>/admin/post/<slug:post_slug>/edit/', views.post_edit, name='post_edit'),
    path('<slug:slug>/admin/post/<slug:post_slug>/delete/', views.post_delete, name='post_delete'),
    path('<slug:slug>/admin/widget/create/', views.widget_create, name='widget_create'),
    path('<slug:slug>/admin/widget/<int:pk>/delete/', views.widget_delete, name='widget_delete'),
    path('<slug:slug>/<slug:post_slug>/comment/', views.post_comment, name='post_comment'),
    path('<slug:slug>/<slug:post_slug>/', views.site_post, name='post'),
]
