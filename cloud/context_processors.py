from django.urls import reverse


def sidebar(request):
    """Provide a universal sidebar with all apps and highlight the active one."""

    items = [
        {'key': 'dashboard', 'label': 'Dashboard', 'icon': '📊', 'url': reverse('dashboard:index')},
        {'key': 'files', 'label': 'Fayllarım', 'icon': '📁', 'url': reverse('files:index')},
        {'key': 'photos', 'label': 'Fotolar', 'icon': '🖼️', 'url': reverse('files:photos')},
        {'key': 'drives', 'label': 'Paylaşılan sürücülər', 'icon': '👥', 'url': reverse('files:drives')},
        {'key': 'office', 'label': 'Ofis', 'icon': '📝', 'url': reverse('office:index')},
        {'key': 'notes', 'label': 'Qeydlər', 'icon': '🗒️', 'url': reverse('notes:index')},
        {'key': 'calendars', 'label': 'Təqvim', 'icon': '📅', 'url': reverse('calendars:index')},
        {'key': 'contacts', 'label': 'Kontaktlar', 'icon': '👥', 'url': reverse('contacts:index')},
        {'key': 'meet', 'label': 'Görüşlər', 'icon': '📹', 'url': reverse('meet:index')},
        {'key': 'chat', 'label': 'Chat', 'icon': '💬', 'url': reverse('chat:index')},
        {'key': 'mail', 'label': 'E-poçt', 'icon': '✉️', 'url': reverse('mail:inbox')},
        {'key': 'tasks', 'label': 'Tapşırıqlar', 'icon': '✅', 'url': reverse('tasks:index')},
        {'key': 'sites', 'label': 'Vebsaytlar', 'icon': '🌐', 'url': reverse('sites:index')},
        {'key': 'ai', 'label': 'CLX', 'icon': '✨', 'url': reverse('ai:index')},
        {'key': 'search', 'label': 'Axtarış', 'icon': '🔍', 'url': reverse('search:index')},
        {'key': 'forms', 'label': 'Anketlər', 'icon': '📋', 'url': reverse('forms:index')},
        {'key': 'forum', 'label': 'Forum', 'icon': '💬', 'url': reverse('forum:index')},
        {'key': 'scheduler', 'label': 'Görüş planlayıcı', 'icon': '📅', 'url': reverse('scheduler:index')},
        {'key': 'links', 'label': 'Qısa linklər', 'icon': '🔗', 'url': reverse('links:index')},
        {'key': 'payments', 'label': 'Plan', 'icon': '💳', 'url': reverse('payments:plan')},
    ]

    path = request.path
    active = None
    for item in items:
        if path.startswith('/' + item['key'] + '/'):
            active = item['key']
            break

    return {'sidebar_items': items, 'active_app': active}
