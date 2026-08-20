import csv
import json
from io import StringIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from files.models import File
from .models import OfficeFile


IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff', '.ico'}
TEXT_EXTENSIONS = {'.txt', '.md', '.html', '.htm', '.xml', '.json', '.py', '.js', '.css', '.csv'}


@login_required
def office_index(request):
    files = OfficeFile.objects.filter(owner=request.user)
    return render(request, 'office/index.html', {'files': files})


@login_required
def office_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip() or 'Adsız sənəd'
        ftype = request.POST.get('type', OfficeFile.TYPE_DOC)
        if ftype not in dict(OfficeFile.TYPE_CHOICES):
            ftype = OfficeFile.TYPE_DOC
        content = ''
        if ftype == OfficeFile.TYPE_SHEET:
            content = json.dumps([[''] * 5 for _ in range(5)])
        elif ftype == OfficeFile.TYPE_SLIDES:
            content = json.dumps([{'title': 'Başlıq', 'body': 'Mətn'}, {'title': 'İkinci slayd', 'body': 'Məzmun'}])
        f = OfficeFile.objects.create(owner=request.user, title=title, type=ftype, content=content)
        messages.success(request, f'{f.title} yaradıldı.')
        return redirect('office:edit', pk=f.id)
    return render(request, 'office/create.html')


@login_required
def office_open_file(request, file_pk):
    """Open an uploaded File inside the Office editor.

    Images -> doc editor embedding the image.
    CSV   -> sheet editor with parsed rows.
    Text  -> doc editor with the raw text content.
    """
    src = get_object_or_404(File, pk=file_pk, owner=request.user)
    name = (src.name or '').lower()
    ext = ''
    if '.' in name:
        ext = '.' + name.rsplit('.', 1)[1]

    if ext == '.csv':
        ftype = OfficeFile.TYPE_SHEET
        try:
            text = src.file.read().decode('utf-8-sig')
        except Exception:
            text = ''
        rows = list(csv.reader(StringIO(text)))
        content = json.dumps(rows)
    elif ext in IMAGE_EXTENSIONS or (src.mime_type or '').startswith('image/'):
        ftype = OfficeFile.TYPE_DOC
        content = f'<p><img src="{src.file.url}" style="max-width:100%"></p>'
    elif ext in TEXT_EXTENSIONS:
        ftype = OfficeFile.TYPE_DOC
        try:
            text = src.file.read().decode('utf-8')
        except Exception:
            text = ''
        content = '<pre style="white-space:pre-wrap;font-family:monospace">' + text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') + '</pre>'
    else:
        messages.error(request, f'{src.name} Office-də açıla bilməyən fayl növüdür.')
        return redirect('files:index')

    f = OfficeFile.objects.create(
        owner=request.user,
        title=src.name,
        type=ftype,
        content=content,
    )
    messages.success(request, f'{src.name} Office-də açıldı.')
    return redirect('office:edit', pk=f.id)


@login_required
def office_edit(request, pk):
    f = get_object_or_404(OfficeFile, pk=pk, owner=request.user)
    if request.method == 'POST':
        f.title = request.POST.get('title', '').strip() or f.title
        f.content = request.POST.get('content', '')
        f.save()
        messages.success(request, 'Yadda saxlandı.')
        return redirect('office:edit', pk=f.id)
    return render(request, 'office/edit.html', {'f': f})


@login_required
def office_delete(request, pk):
    f = get_object_or_404(OfficeFile, pk=pk, owner=request.user)
    title = f.title
    f.delete()
    messages.success(request, f'{title} silindi.')
    return redirect('office:index')


@login_required
def office_export(request, pk):
    f = get_object_or_404(OfficeFile, pk=pk, owner=request.user)
    if f.type == OfficeFile.TYPE_DOC:
        html = f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>{f.title}</title></head><body>{f.content}</body></html>'
        return HttpResponse(html, content_type='text/html; charset=utf-8',
                            headers={'Content-Disposition': f'attachment; filename="{f.title}.html"'})
    if f.type == OfficeFile.TYPE_SHEET:
        try:
            data = json.loads(f.content)
        except (ValueError, TypeError):
            data = []
        import csv
        from io import StringIO
        buf = StringIO()
        writer = csv.writer(buf)
        for row in data:
            writer.writerow(row)
        return HttpResponse(buf.getvalue(), content_type='text/csv; charset=utf-8',
                            headers={'Content-Disposition': f'attachment; filename="{f.title}.csv"'})
    if f.type == OfficeFile.TYPE_SLIDES:
        try:
            slides = json.loads(f.content)
        except (ValueError, TypeError):
            slides = []
        body = ''.join(
            f'<section><h1>{s.get("title", "")}</h1><p>{s.get("body", "")}</p></section>'
            for s in slides
        )
        html = f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>{f.title}</title>'
        html += '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.1/dist/reveal.css">'
        html += '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.1/dist/theme/black.css">'
        html += '</head><body><div class="reveal"><div class="slides">' + body + '</div></div>'
        html += '<script src="https://cdn.jsdelivr.net/npm/reveal.js@4.6.1/dist/reveal.js"></script>'
        html += '<script>Reveal.initialize();</script></body></html>'
        return HttpResponse(html, content_type='text/html; charset=utf-8',
                            headers={'Content-Disposition': f'attachment; filename="{f.title}.html"'})
    return redirect('office:index')
