import re
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Category, ChatMessage, Post, Thread


def _strip_html(value):
    return re.sub(r'<[^>]+>', '', value or '').strip()


def forum_index(request):
    categories = Category.objects.all()
    return render(request, 'forum/index.html', {'categories': categories})


def forum_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    threads = category.threads.all()
    return render(request, 'forum/category.html', {'category': category, 'threads': threads})


@login_required
def forum_create_thread(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '')
        if title and _strip_html(body):
            Thread.objects.create(category=category, author=request.user, title=title, body=body)
            messages.success(request, 'Mövzu yaradıldı.')
            return redirect('forum:category', pk=category.id)
        messages.error(request, 'Başlıq və mətn daxil edin.')
    return render(request, 'forum/create_thread.html', {'category': category})


def forum_thread(request, pk):
    thread = get_object_or_404(Thread, pk=pk)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'Cavab yazmaq üçün daxil olun.')
            return redirect('accounts:login')
        body = request.POST.get('body', '')
        if _strip_html(body):
            Post.objects.create(thread=thread, author=request.user, body=body)
            messages.success(request, 'Cavab əlavə edildi.')
        return redirect('forum:thread', pk=thread.id)
    return render(request, 'forum/thread.html', {'thread': thread})


@login_required
def forum_upload(request):
    """Upload an image/GIF for the rich text editor. Returns JSON with URL."""
    if request.method == 'POST' and request.FILES.get('file'):
        f = request.FILES['file']
        ext = ''
        if '.' in f.name:
            ext = f.name.rsplit('.', 1)[1].lower()
        allowed = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'}
        if ext not in allowed:
            return JsonResponse({'error': 'Yalnız şəkil faylları (jpg, png, gif, webp) icazəlidir.'}, status=400)
        f.name = f'forum_{uuid.uuid4().hex[:12]}.{ext}'
        from django.core.files.storage import default_storage
        path = default_storage.save('forum_uploads/' + f.name, f)
        url = default_storage.url(path)
        return JsonResponse({'url': url})
    return JsonResponse({'error': 'Fayl göndərilmədi.'}, status=400)


def forum_chat(request):
    messages_list = ChatMessage.objects.all()[:200]
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'Chatda yazmaq üçün daxil olun.')
            return redirect('accounts:login')
        body = request.POST.get('body', '').strip()
        if body:
            ChatMessage.objects.create(author=request.user, body=body)
        return redirect('forum:chat')
    return render(request, 'forum/chat.html', {'chat_messages': messages_list})
