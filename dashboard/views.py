from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard_index(request):
    u = request.user

    from files.models import File, Folder, Album, SharedDrive
    from notes.models import Note
    from contacts.models import Contact
    from chat.models import Message as ChatMessage
    from mail.models import EmailMessage
    from tasks.models import Task, TaskList
    from sites.models import Site, Post
    from scheduler.models import ScheduleLink, Booking
    from links.models import ShortLink

    files = File.objects.filter(owner=u)
    total_used = sum(f.size for f in files)
    limit = u.storage_limit_mb * 1024 * 1024

    stats = {
        'files': files.count(),
        'folders': Folder.objects.filter(owner=u).count(),
        'photos': sum(1 for f in files if (f.mime_type or '').startswith('image/')),
        'albums': Album.objects.filter(owner=u).count(),
        'drives': SharedDrive.objects.filter(owner=u).count() + SharedDrive.objects.filter(members=u).distinct().count(),
        'notes': Note.objects.filter(owner=u).count(),
        'contacts': Contact.objects.filter(owner=u).count(),
        'chat_messages': ChatMessage.objects.filter(author=u).count(),
        'emails_sent': EmailMessage.objects.filter(sender=u).count(),
        'tasks': Task.objects.filter(task_list__owner=u).count(),
        'task_lists': TaskList.objects.filter(owner=u).count(),
        'sites': Site.objects.filter(owner=u).count(),
        'posts': Post.objects.filter(site__owner=u).count(),
        'schedule_links': ScheduleLink.objects.filter(owner=u).count(),
        'bookings': Booking.objects.filter(schedule__owner=u).count(),
        'short_links': ShortLink.objects.filter(owner=u).count(),
        'total_used': total_used,
        'limit': limit,
        'percent': int((total_used / limit) * 100) if limit else 0,
    }

    return render(request, 'dashboard/index.html', {'stats': stats})
