from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing, name='landing'),
    path('accounts/', include('accounts.urls')),
    path('files/', include('files.urls')),
    path('office/', include('office.urls')),
    path('notes/', include('notes.urls')),
    path('calendars/', include('calendars.urls')),
    path('forms/', include('forms.urls')),
    path('forum/', include('forum.urls')),
    path('contacts/', include('contacts.urls')),
    path('meet/', include('meet.urls')),
    path('chat/', include('chat.urls')),
    path('search/', include('search.urls')),
    path('mail/', include('mail.urls')),
    path('tasks/', include('tasks.urls')),
    path('cites/', include('sites.urls')),
    path('ai/', include('ai.urls')),
    path('scheduler/', include('scheduler.urls')),
    path('links/', include('links.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('payments/', include('payments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
