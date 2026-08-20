from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Conversation, Message
from .services import DEFAULT_SYSTEM_PROMPT, get_ai_response, get_ollama_models


@login_required
def ai_index(request, conv_id=None):
    conversations = Conversation.objects.filter(user=request.user)
    current = None
    if conv_id:
        current = get_object_or_404(Conversation, pk=conv_id, user=request.user)
    elif conversations.exists():
        current = conversations.first()
    msgs = current.messages.all() if current else Message.objects.none()
    models, models_error = get_ollama_models()
    return render(request, 'ai/index.html', {
        'conversations': conversations,
        'current': current,
        'messages': msgs,
        'models': models,
        'models_error': models_error,
        'default_system_prompt': DEFAULT_SYSTEM_PROMPT,
    })


@login_required
def ai_new(request):
    conv = Conversation.objects.create(user=request.user, title='Yeni söhbət')
    return redirect('ai:chat', conv_id=conv.id)


@login_required
def ai_delete(request, conv_id):
    conv = get_object_or_404(Conversation, pk=conv_id, user=request.user)
    conv.delete()
    messages.success(request, 'Söhbət silindi.')
    return redirect('ai:index')


@login_required
def ai_send(request, conv_id):
    conv = get_object_or_404(Conversation, pk=conv_id, user=request.user)
    if request.method == 'POST':
        content = request.POST.get('message', '').strip()
        model = request.POST.get('model', '').strip()
        system_prompt = request.POST.get('system_prompt', '').strip()
        attachment = request.FILES.get('attachment')

        if model:
            conv.model = model
        if system_prompt:
            conv.system_prompt = system_prompt
        conv.save(update_fields=['model', 'system_prompt', 'updated_at'])

        if content or attachment:
            user_msg = Message.objects.create(
                conversation=conv, role=Message.ROLE_USER, content=content,
                attachment=attachment,
                attachment_name=attachment.name if attachment else '',
            )
            if conv.title == 'Yeni söhbət':
                conv.title = (content or attachment.name or 'Yeni söhbət')[:50]
                conv.save(update_fields=['title'])

            history = [
                {'role': m.role, 'content': m.content}
                for m in conv.messages.all()
            ]
            reply, error = get_ai_response(history, model=conv.model or None, system_prompt=conv.system_prompt or None)
            if error:
                Message.objects.create(conversation=conv, role=Message.ROLE_ASSISTANT, content=f'⚠️ {error}')
            else:
                Message.objects.create(conversation=conv, role=Message.ROLE_ASSISTANT, content=reply)
            conv.save(update_fields=['updated_at'])
    return redirect('ai:chat', conv_id=conv.id)


@login_required
def ai_send_ajax(request, conv_id):
    """AJAX endpoint: send a message and return the assistant reply as JSON."""
    conv = get_object_or_404(Conversation, pk=conv_id, user=request.user)
    if request.method != 'POST':
        return JsonResponse({'error': 'Yalnız POST.'}, status=405)

    content = request.POST.get('message', '').strip()
    model = request.POST.get('model', '').strip()
    system_prompt = request.POST.get('system_prompt', '').strip()
    attachment = request.FILES.get('attachment')

    if model:
        conv.model = model
    if system_prompt:
        conv.system_prompt = system_prompt
    conv.save(update_fields=['model', 'system_prompt', 'updated_at'])

    if not content and not attachment:
        return JsonResponse({'error': 'Mesaj daxil edin.'}, status=400)

    user_msg = Message.objects.create(
        conversation=conv, role=Message.ROLE_USER, content=content,
        attachment=attachment,
        attachment_name=attachment.name if attachment else '',
    )
    if conv.title == 'Yeni söhbət':
        conv.title = (content or attachment.name or 'Yeni söhbət')[:50]
        conv.save(update_fields=['title'])

    history = [
        {'role': m.role, 'content': m.content}
        for m in conv.messages.all()
    ]
    reply, error = get_ai_response(history, model=conv.model or None, system_prompt=conv.system_prompt or None)
    if error:
        assistant_content = f'⚠️ {error}'
    else:
        assistant_content = reply
    assistant = Message.objects.create(conversation=conv, role=Message.ROLE_ASSISTANT, content=assistant_content)
    conv.save(update_fields=['updated_at'])

    return JsonResponse({
        'user': {
            'id': user_msg.id,
            'content': user_msg.content,
            'attachment_name': user_msg.attachment_name,
            'attachment_url': user_msg.attachment.url if user_msg.attachment else None,
            'created_at': user_msg.created_at.strftime('%H:%M'),
        },
        'assistant': {
            'id': assistant.id,
            'content': assistant.content,
            'created_at': assistant.created_at.strftime('%H:%M'),
        },
        'title': conv.title,
    })
