from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from calendars.models import Notification
from .models import Meeting, MeetingInvite


@login_required
def meet_index(request):
    meetings = Meeting.objects.filter(owner=request.user)
    invited = MeetingInvite.objects.filter(invitee=request.user).select_related('meeting')
    return render(request, 'meet/index.html', {
        'meetings': meetings,
        'invited': invited,
        'other_users': User.objects.exclude(pk=request.user.pk),
    })


@login_required
def meet_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip() or 'Yeni görüş'
        meeting = Meeting.objects.create(owner=request.user, title=title)
        # Invite selected users and notify them.
        for uid in request.POST.getlist('invitees'):
            try:
                invitee = User.objects.get(pk=uid)
            except (User.DoesNotExist, ValueError):
                continue
            if invitee == request.user:
                continue
            inv, created = MeetingInvite.objects.get_or_create(meeting=meeting, invitee=invitee)
            if created:
                Notification.objects.create(
                    recipient=invitee,
                    text=f'{request.user.username} sizi "{meeting.title}" görüşünə çağırdı.',
                    link=f'/meet/{meeting.id}/',
                )
        messages.success(request, 'Görüş yaradıldı.')
        return redirect('meet:join', pk=meeting.id)
    return redirect('meet:index')


@login_required
def meet_join(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    is_owner = meeting.owner == request.user
    if not is_owner:
        invited = MeetingInvite.objects.filter(meeting=meeting, invitee=request.user).exists()
        if not invited:
            messages.error(request, 'Bu görüşə qoşulma icazəniz yoxdur.')
            return redirect('meet:index')
    return render(request, 'meet/join.html', {'meeting': meeting})


@login_required
def meet_delete(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk, owner=request.user)
    meeting.delete()
    messages.success(request, 'Görüş silindi.')
    return redirect('meet:index')
