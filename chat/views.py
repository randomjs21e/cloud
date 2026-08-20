import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from calendars.models import Notification
from contacts.models import Contact
from .models import ChatGroup, Conversation, Membership, Message


@login_required
def chat_index(request):
    groups = ChatGroup.objects.filter(members=request.user)
    conversations = Conversation.objects.filter(user1=request.user) | Conversation.objects.filter(user2=request.user)
    conv_list = [(conv, conv.other(request.user)) for conv in conversations]
    return render(request, 'chat/index.html', {
        'groups': groups,
        'conversations': conv_list,
        'other_users': User.objects.exclude(pk=request.user.pk),
    })


@login_required
def chat_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip() or 'Yeni qrup'
        group = ChatGroup.objects.create(owner=request.user, name=name)
        Membership.objects.create(group=group, user=request.user)
        for uid in request.POST.getlist('members'):
            try:
                u = User.objects.get(pk=uid)
            except (User.DoesNotExist, ValueError):
                continue
            if u == request.user:
                continue
            Membership.objects.get_or_create(group=group, user=u)
        messages.success(request, f'{name} qrupu yaradıldı.')
        return redirect('chat:room', pk=group.id)
    return redirect('chat:index')


@login_required
def chat_room(request, pk):
    group = get_object_or_404(ChatGroup, pk=pk)
    if not group.members.filter(pk=request.user.pk).exists():
        messages.error(request, 'Bu qrupa daxil deyilsiniz.')
        return redirect('chat:index')
    if request.method == 'POST':
        _create_message(request, group=group)
        return redirect('chat:room', pk=group.id)
    messages_list = group.messages.all()
    return render(request, 'chat/room.html', {
        'group': group,
        'messages': messages_list,
        'is_private': False,
        'my_contacts': Contact.objects.filter(owner=request.user),
    })


@login_required
def chat_private(request, user_id):
    other = get_object_or_404(User, pk=user_id)
    if other == request.user:
        return redirect('chat:index')
    conv = Conversation.get_or_create_between(request.user, other)
    if request.method == 'POST':
        _create_message(request, conversation=conv)
        return redirect('chat:private', user_id=other.id)
    messages_list = conv.messages.all()
    return render(request, 'chat/room.html', {
        'group': None,
        'conversation': conv,
        'other': other,
        'messages': messages_list,
        'is_private': True,
        'my_contacts': Contact.objects.filter(owner=request.user),
    })


def _create_message(request, group=None, conversation=None):
    mtype = request.POST.get('type', Message.TYPE_TEXT)
    body = request.POST.get('body', '').strip()
    attachment = request.FILES.get('attachment')
    contact_name = request.POST.get('contact_name', '').strip()
    contact_phone = request.POST.get('contact_phone', '').strip()

    if mtype == Message.TYPE_IMAGE and attachment:
        Message.objects.create(group=group, conversation=conversation, author=request.user,
                               type=Message.TYPE_IMAGE, attachment=attachment)
    elif mtype == Message.TYPE_FILE and attachment:
        Message.objects.create(group=group, conversation=conversation, author=request.user,
                               type=Message.TYPE_FILE, attachment=attachment, body=attachment.name)
    elif mtype == Message.TYPE_VOICE and attachment:
        Message.objects.create(group=group, conversation=conversation, author=request.user,
                               type=Message.TYPE_VOICE, attachment=attachment)
    elif mtype == Message.TYPE_CONTACT and contact_name:
        Message.objects.create(group=group, conversation=conversation, author=request.user,
                               type=Message.TYPE_CONTACT, contact_name=contact_name, contact_phone=contact_phone)
    elif body:
        Message.objects.create(group=group, conversation=conversation, author=request.user,
                               type=Message.TYPE_TEXT, body=body)


@login_required
def chat_upload(request):
    """Upload an attachment (image/file/voice) for chat. Returns JSON with URL."""
    if request.method == 'POST' and request.FILES.get('file'):
        f = request.FILES['file']
        f.name = f'chat_{uuid.uuid4().hex[:12]}_{f.name}'
        from django.core.files.storage import default_storage
        path = default_storage.save('chat_uploads/' + f.name, f)
        return JsonResponse({'url': default_storage.url(path)})
    return JsonResponse({'error': 'Fayl göndərilmədi.'}, status=400)


@login_required
def chat_notifications_api(request):
    """JSON endpoint: recent chat messages for the current user (for toast alerts)."""
    group_ids = ChatGroup.objects.filter(members=request.user).values_list('id', flat=True)
    conv_ids = Conversation.objects.filter(user1=request.user).values_list('id', flat=True) | \
               Conversation.objects.filter(user2=request.user).values_list('id', flat=True)
    recent = Message.objects.filter(
        models.Q(group_id__in=group_ids) | models.Q(conversation_id__in=conv_ids)
    ).exclude(author=request.user).order_by('-created_at')[:10]
    data = []
    for m in recent:
        if m.group:
            target = {'type': 'group', 'name': m.group.name, 'url': f'/chat/{m.group.id}/'}
        elif m.conversation:
            other = m.conversation.other(request.user)
            target = {'type': 'private', 'name': other.get_full_name() or other.username, 'url': f'/chat/private/{other.id}/'}
        else:
            continue
        data.append({
            'id': m.id,
            'author': m.author.get_full_name() or m.author.username,
            'type': m.type,
            'body': m.body,
            'created_at': m.created_at.strftime('%H:%M'),
            'target': target,
        })
    return JsonResponse({'messages': data})


@login_required
def chat_delete(request, pk):
    group = get_object_or_404(ChatGroup, pk=pk, owner=request.user)
    group.delete()
    messages.success(request, 'Qrup silindi.')
    return redirect('chat:index')
