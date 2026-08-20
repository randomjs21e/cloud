from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Booking, ScheduleLink


@login_required
def scheduler_index(request):
    links = ScheduleLink.objects.filter(owner=request.user)
    return render(request, 'scheduler/index.html', {'links': links})


@login_required
def scheduler_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if not title:
            messages.error(request, 'Başlıq daxil edin.')
            return redirect('scheduler:index')
        try:
            duration = int(request.POST.get('duration', 30))
        except ValueError:
            duration = 30
        ScheduleLink.objects.create(
            owner=request.user,
            title=title,
            duration_minutes=max(5, min(duration, 240)),
            description=request.POST.get('description', '').strip(),
        )
        messages.success(request, 'Görüş linki yaradıldı.')
        return redirect('scheduler:index')
    return redirect('scheduler:index')


@login_required
def scheduler_delete(request, pk):
    link = get_object_or_404(ScheduleLink, pk=pk, owner=request.user)
    link.delete()
    messages.success(request, 'Görüş linki silindi.')
    return redirect('scheduler:index')


@login_required
def scheduler_bookings(request, pk):
    link = get_object_or_404(ScheduleLink, pk=pk, owner=request.user)
    return render(request, 'scheduler/bookings.html', {'link': link, 'bookings': link.bookings.all()})


def scheduler_public(request, slug):
    link = get_object_or_404(ScheduleLink, slug=slug, is_active=True)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        start = request.POST.get('start_time', '')
        if not name or not start:
            messages.error(request, 'Ad və vaxt daxil edin.')
            return redirect('scheduler:public', slug=link.slug)
        from django.utils.dateparse import parse_datetime
        start_dt = parse_datetime(start)
        if not start_dt:
            messages.error(request, 'Yanlış vaxt formatı.')
            return redirect('scheduler:public', slug=link.slug)
        if start_dt < timezone.now():
            messages.error(request, 'Keçmiş vaxt seçilə bilməz.')
            return redirect('scheduler:public', slug=link.slug)
        Booking.objects.create(
            schedule=link, name=name,
            email=request.POST.get('email', '').strip(),
            notes=request.POST.get('notes', '').strip(),
            start_time=start_dt,
        )
        messages.success(request, 'Görüş təyin edildi!')
        return redirect('scheduler:public', slug=link.slug)

    # Build available slots for the next 7 days (9:00-17:00, hourly).
    slots = []
    now = timezone.now()
    for day in range(7):
        day_start = (now + timedelta(days=day)).replace(hour=9, minute=0, second=0, microsecond=0)
        for hour in range(8):
            slot = day_start + timedelta(hours=hour)
            if slot <= now:
                continue
            slots.append(slot)
    return render(request, 'scheduler/public.html', {'link': link, 'slots': slots})
