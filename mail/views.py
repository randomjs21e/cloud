from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from .models import EmailMessage, EmailRecipient


@login_required
def mail_index(request):
    return redirect('mail:inbox')


@login_required
def mail_inbox(request):
    links = EmailRecipient.objects.filter(user=request.user, is_deleted=False, is_archived=False).select_related('email', 'email__sender')
    return render(request, 'mail/index.html', {
        'folder': 'inbox',
        'emails': [l.email for l in links],
        'unread_count': links.filter(is_read=False).count(),
    })


@login_required
def mail_sent(request):
    emails = EmailMessage.objects.filter(sender=request.user)
    return render(request, 'mail/index.html', {
        'folder': 'sent',
        'emails': emails,
        'unread_count': 0,
    })


@login_required
def mail_starred(request):
    links = EmailRecipient.objects.filter(user=request.user, is_starred=True, is_deleted=False).select_related('email', 'email__sender')
    return render(request, 'mail/index.html', {
        'folder': 'starred',
        'emails': [l.email for l in links],
        'unread_count': 0,
    })


@login_required
def mail_archived(request):
    links = EmailRecipient.objects.filter(user=request.user, is_archived=True, is_deleted=False).select_related('email', 'email__sender')
    return render(request, 'mail/index.html', {
        'folder': 'archived',
        'emails': [l.email for l in links],
        'unread_count': 0,
    })


@login_required
def mail_trash(request):
    links = EmailRecipient.objects.filter(user=request.user, is_deleted=True).select_related('email', 'email__sender')
    return render(request, 'mail/index.html', {
        'folder': 'trash',
        'emails': [l.email for l in links],
        'unread_count': 0,
    })


@login_required
def mail_compose(request):
    if request.method == 'POST':
        to_raw = request.POST.get('to', '').strip()
        subject = request.POST.get('subject', '').strip()
        body = request.POST.get('body', '')
        if not to_raw:
            messages.error(request, 'Alıcı daxil edin.')
            return redirect('mail:compose')
        recipients = []
        for token in to_raw.replace(';', ',').split(','):
            token = token.strip()
            if not token:
                continue
            u = User.objects.filter(username=token).first() or User.objects.filter(email=token).first()
            if not u:
                messages.error(request, f'"{token}" istifadəçisi tapılmadı.')
                return redirect('mail:compose')
            if u not in recipients:
                recipients.append(u)
        email = EmailMessage.objects.create(sender=request.user, subject=subject, body=body)
        for u in recipients:
            EmailRecipient.objects.create(email=email, user=u)
        messages.success(request, 'E-poçt göndərildi.')
        return redirect('mail:sent')
    return render(request, 'mail/compose.html', {
        'users': User.objects.exclude(pk=request.user.pk),
    })


@login_required
def mail_detail(request, pk):
    email = get_object_or_404(EmailMessage, pk=pk)
    link = EmailRecipient.objects.filter(email=email, user=request.user).first()
    is_sender = email.sender == request.user
    if not link and not is_sender:
        messages.error(request, 'Bu e-poçta girişiniz yoxdur.')
        return redirect('mail:inbox')
    if link and not link.is_read:
        link.is_read = True
        link.save(update_fields=['is_read'])
    return render(request, 'mail/detail.html', {
        'email': email,
        'link': link,
        'is_sender': is_sender,
    })


@login_required
def mail_action(request, pk):
    email = get_object_or_404(EmailMessage, pk=pk)
    action = request.POST.get('action', '')
    link = EmailRecipient.objects.filter(email=email, user=request.user).first()
    if link:
        if action == 'delete':
            link.is_deleted = True
        elif action == 'restore':
            link.is_deleted = False
        elif action == 'star':
            link.is_starred = not link.is_starred
        elif action == 'archive':
            link.is_archived = True
            link.is_deleted = False
        elif action == 'unarchive':
            link.is_archived = False
        link.save()
    elif email.sender == request.user and action == 'delete':
        email.delete()
    return redirect(request.POST.get('next') or 'mail:inbox')
