import re

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from calendars.models import Event
from chat.models import ChatGroup, Message
from contacts.models import Contact
from files.models import File
from forms.models import Survey
from forum.models import Thread, Post
from meet.models import Meeting
from notes.models import Note
from office.models import OfficeFile

from .aisearch import ask_ai
from .websearch import search_web


def _strip_html(value):
    return re.sub(r'<[^>]+>', ' ', value or '')


@login_required
def search_index(request):
    q = request.GET.get('q', '').strip()
    mode = request.GET.get('mode', 'all')
    results = []
    web_results = []
    web_error = None

    if q:
        # Internal search (all modes except 'web')
        if mode in ('all', 'internal'):
            results = _internal_search(request, q)

        # Web search
        if mode in ('all', 'web'):
            web_results, web_error = search_web(q)

        # AI answer is loaded asynchronously via /search/ai/ so it never blocks the page.

    return render(request, 'search/index.html', {
        'q': q,
        'mode': mode,
        'results': results,
        'web_results': web_results,
        'web_error': web_error,
    })


@login_required
def search_ai_ajax(request):
    """JSON endpoint: AI answer for a query (loaded asynchronously)."""
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'answer': None, 'error': None})
    web_results, _ = search_web(q)
    context = '\n'.join(
        f"- {r['title']}: {r['snippet']} ({r['url']})" for r in web_results[:5]
    ) if web_results else None
    ai_answer, ai_error = ask_ai(q, context=context)
    return JsonResponse({'answer': ai_answer, 'error': ai_error})


def _internal_search(request, q):
    results = []
    if q:
        # Files (name + content)
        for f in File.objects.filter(owner=request.user, name__icontains=q):
            results.append({'type': 'Fayl', 'icon': '📁', 'title': f.name, 'snippet': f.mime_type, 'url': f'/files/'})
        # Notes
        for n in Note.objects.filter(owner=request.user).filter(title__icontains=q) | Note.objects.filter(owner=request.user, body__icontains=q):
            results.append({'type': 'Qeyd', 'icon': '🗒️', 'title': n.title or 'Qeyd', 'snippet': _strip_html(n.body)[:120], 'url': f'/notes/{n.id}/'})
        # Office files
        for o in OfficeFile.objects.filter(owner=request.user).filter(title__icontains=q) | OfficeFile.objects.filter(owner=request.user, content__icontains=q):
            results.append({'type': 'Ofis', 'icon': '📝', 'title': o.title, 'snippet': _strip_html(o.content)[:120], 'url': f'/office/{o.id}/'})
        # Contacts
        for c in Contact.objects.filter(owner=request.user).filter(name__icontains=q) | Contact.objects.filter(owner=request.user, phone__icontains=q) | Contact.objects.filter(owner=request.user, email__icontains=q):
            results.append({'type': 'Kontakt', 'icon': '👥', 'title': c.name, 'snippet': f'{c.phone} {c.email}'.strip(), 'url': f'/contacts/'})
        # Calendar events
        for e in Event.objects.filter(owner=request.user).filter(title__icontains=q) | Event.objects.filter(owner=request.user, description__icontains=q):
            results.append({'type': 'Təqvim', 'icon': '📅', 'title': e.title, 'snippet': f'{e.date} {e.description}'.strip(), 'url': f'/calendars/{e.id}/'})
        # Surveys
        for s in Survey.objects.filter(owner=request.user).filter(title__icontains=q) | Survey.objects.filter(owner=request.user, description__icontains=q):
            results.append({'type': 'Anket', 'icon': '📋', 'title': s.title, 'snippet': s.description, 'url': f'/forms/{s.id}/'})
        # Meetings
        for m in Meeting.objects.filter(owner=request.user).filter(title__icontains=q):
            results.append({'type': 'Görüş', 'icon': '📹', 'title': m.title, 'snippet': m.room, 'url': f'/meet/{m.id}/'})
        # Forum threads (own + all public)
        for t in Thread.objects.filter(title__icontains=q) | Thread.objects.filter(body__icontains=q):
            results.append({'type': 'Forum mövzusu', 'icon': '🗣️', 'title': t.title, 'snippet': _strip_html(t.body)[:120], 'url': f'/forum/thread/{t.id}/'})
        for p in Post.objects.filter(body__icontains=q):
            results.append({'type': 'Forum cavabı', 'icon': '💬', 'title': f'{p.thread.title}', 'snippet': _strip_html(p.body)[:120], 'url': f'/forum/thread/{p.thread.id}/'})
        # Chat groups + messages (groups user is in)
        for g in ChatGroup.objects.filter(members=request.user).filter(name__icontains=q):
            results.append({'type': 'Chat qrupu', 'icon': '💬', 'title': g.name, 'snippet': f'{g.members.count} üzv', 'url': f'/chat/{g.id}/'})
        for msg in Message.objects.filter(group__members=request.user, body__icontains=q):
            results.append({'type': 'Chat mesajı', 'icon': '💬', 'title': msg.group.name, 'snippet': f'{msg.author.username}: {msg.body[:120]}', 'url': f'/chat/{msg.group.id}/'})

    return results
