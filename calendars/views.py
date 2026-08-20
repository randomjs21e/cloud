import calendar
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from .models import Event, Invitation, Notification


def _visible_events(user, year, month):
    """Events the user can see: owned or accepted invitations in the month."""
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    owned = Event.objects.filter(owner=user, date__gte=start, date__lt=end)
    invited_ids = Invitation.objects.filter(
        invitee=user, status=Invitation.ACCEPTED, event__date__gte=start, event__date__lt=end
    ).values_list('event_id', flat=True)
    invited = Event.objects.filter(id__in=invited_ids)
    return owned, invited


@login_required
def calendars_index(request):
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    try:
        month = max(1, min(12, month))
    except Exception:
        month = today.month

    owned, invited = _visible_events(request.user, year, month)
    events_by_day = {}
    for e in owned:
        events_by_day.setdefault(e.date.day, []).append((e, True))
    for e in invited:
        events_by_day.setdefault(e.date.day, []).append((e, False))

    cal = calendar.Calendar(firstweekday=0)
    weeks = []
    for week in cal.monthdayscalendar(year, month):
        cells = []
        for day in week:
            cells.append({'day': day, 'events': events_by_day.get(day, [])})
        weeks.append(cells)

    prev = (year, month - 1) if month > 1 else (year - 1, 12)
    nxt = (year, month + 1) if month < 12 else (year + 1, 1)

    return render(request, 'calendars/index.html', {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'day_names': ['B.e', 'Ç.a', 'Çər', 'C.a', 'Cümə', 'Şən', 'Baz'],
        'weeks': weeks,
        'today': today,
        'prev': prev,
        'nxt': nxt,
        'other_users': User.objects.exclude(pk=request.user.pk),
    })


@login_required
def calendars_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip() or 'Hadisə'
        date_str = request.POST.get('date', '')
        time_str = request.POST.get('time', '') or None
        description = request.POST.get('description', '')
        if not date_str:
            messages.error(request, 'Tarix seçin.')
            return redirect('calendars:index')
        try:
            ev_date = date.fromisoformat(date_str)
        except ValueError:
            messages.error(request, 'Yanlış tarix.')
            return redirect('calendars:index')
        ev = Event.objects.create(
            owner=request.user,
            title=title,
            description=description,
            date=ev_date,
            time=time_str,
        )
        # Tag other users: send invitation + notification to each.
        invited_ids = request.POST.getlist('invitees')
        for uid in invited_ids:
            try:
                invitee = User.objects.get(pk=uid)
            except (User.DoesNotExist, ValueError):
                continue
            if invitee == request.user:
                continue
            inv, created = Invitation.objects.get_or_create(event=ev, invitee=invitee)
            if created:
                Notification.objects.create(
                    recipient=invitee,
                    text=f'{request.user.username} sizi "{ev.title}" hadisəsinə dəvət etdi ({ev.date}).',
                    link=f'/calendars/invitation/{inv.id}/',
                )
        messages.success(request, f'{ev.title} hadisəsi yaradıldı.')
        return redirect('calendars:index')
    return redirect('calendars:index')


@login_required
def calendars_edit(request, pk):
    ev = get_object_or_404(Event, pk=pk, owner=request.user)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip() or ev.title
        date_str = request.POST.get('date', '')
        time_str = request.POST.get('time', '') or None
        description = request.POST.get('description', '')
        if date_str:
            try:
                ev.date = date.fromisoformat(date_str)
            except ValueError:
                messages.error(request, 'Yanlış tarix.')
                return redirect('calendars:edit', pk=ev.id)
        ev.title = title
        ev.time = time_str
        ev.description = description
        ev.save()
        # Update tagged users: remove old invitations, add new ones.
        ev.invitations.all().delete()
        for uid in request.POST.getlist('invitees'):
            try:
                invitee = User.objects.get(pk=uid)
            except (User.DoesNotExist, ValueError):
                continue
            if invitee == request.user:
                continue
            inv, created = Invitation.objects.get_or_create(event=ev, invitee=invitee)
            if created:
                Notification.objects.create(
                    recipient=invitee,
                    text=f'{request.user.username} sizi "{ev.title}" hadisəsinə dəvət etdi ({ev.date}).',
                    link=f'/calendars/invitation/{inv.id}/',
                )
        messages.success(request, 'Hadisə yeniləndi.')
        return redirect('calendars:detail', pk=ev.id)
    return render(request, 'calendars/edit.html', {
        'event': ev,
        'other_users': User.objects.exclude(pk=request.user.pk),
        'current_invitees': list(ev.invitations.values_list('invitee_id', flat=True)),
    })


@login_required
def calendars_detail(request, pk):
    ev = get_object_or_404(Event, pk=pk)
    is_owner = ev.owner == request.user
    if not is_owner:
        inv = Invitation.objects.filter(event=ev, invitee=request.user, status=Invitation.ACCEPTED).first()
        if not inv:
            messages.error(request, 'Bu hadisəyə baxmaq icazəniz yoxdur.')
            return redirect('calendars:index')
    invitations = ev.invitations.all()
    return render(request, 'calendars/detail.html', {
        'event': ev,
        'is_owner': is_owner,
        'invitations': invitations,
    })


@login_required
def calendars_delete(request, pk):
    ev = get_object_or_404(Event, pk=pk, owner=request.user)
    ev.delete()
    messages.success(request, 'Hadisə silindi.')
    return redirect('calendars:index')


@login_required
def invitation_respond(request, pk):
    inv = get_object_or_404(Invitation, pk=pk, invitee=request.user)
    action = request.POST.get('action', '')
    if action == 'accept':
        inv.status = Invitation.ACCEPTED
        inv.save()
        messages.success(request, f'"{inv.event.title}" hadisəsini qəbul etdiniz. Təqvimdə görünəcək.')
    elif action == 'decline':
        inv.status = Invitation.DECLINED
        inv.save()
        messages.info(request, f'"{inv.event.title}" hadisəsini rədd etdiniz.')
    return redirect('calendars:index')


@login_required
def notifications_index(request):
    notifs = Notification.objects.filter(recipient=request.user)
    notifs.update(is_read=True)
    return render(request, 'calendars/notifications.html', {'notifications': notifs})
