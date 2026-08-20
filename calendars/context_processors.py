def unread_notifications(request):
    if request.user.is_authenticated:
        from .models import Notification
        return {'unread_count': Notification.objects.filter(recipient=request.user, is_read=False).count()}
    return {'unread_count': 0}
