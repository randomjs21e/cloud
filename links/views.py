from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import ShortLink


@login_required
def links_index(request):
    links = ShortLink.objects.filter(owner=request.user)
    return render(request, 'links/index.html', {'links': links})


@login_required
def links_create(request):
    if request.method == 'POST':
        target = request.POST.get('target', '').strip()
        if not target:
            messages.error(request, 'Hədəf link daxil edin.')
            return redirect('links:index')
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        ShortLink.objects.create(
            owner=request.user,
            target=target,
            title=request.POST.get('title', '').strip(),
        )
        messages.success(request, 'Qısa link yaradıldı.')
        return redirect('links:index')
    return redirect('links:index')


@login_required
def links_delete(request, pk):
    link = get_object_or_404(ShortLink, pk=pk, owner=request.user)
    link.delete()
    messages.success(request, 'Link silindi.')
    return redirect('links:index')


def links_redirect(request, code):
    link = get_object_or_404(ShortLink, code=code)
    link.clicks += 1
    link.save(update_fields=['clicks'])
    return redirect(link.target)
