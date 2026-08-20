from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Comment, Post, Site, Widget


@login_required
def sites_index(request):
    sites = Site.objects.filter(owner=request.user)
    return render(request, 'sites/index.html', {'sites': sites})


@login_required
def sites_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'Sayt adı daxil edin.')
            return redirect('sites:index')
        site = Site.objects.create(owner=request.user, name=name)
        messages.success(request, f'"{name}" saytı yaradıldı.')
        return redirect('sites:dashboard', slug=site.slug)
    return redirect('sites:index')


@login_required
def sites_dashboard(request, slug):
    site = get_object_or_404(Site, slug=slug, owner=request.user)
    return render(request, 'sites/dashboard.html', {
        'site': site,
        'posts': site.posts.all(),
    })


@login_required
def sites_edit(request, slug):
    site = get_object_or_404(Site, slug=slug, owner=request.user)
    if request.method == 'POST':
        site.title = request.POST.get('title', '').strip() or site.name
        site.tagline = request.POST.get('tagline', '').strip()
        site.theme = request.POST.get('theme', site.theme)
        site.ad_code = request.POST.get('ad_code', '').strip()
        site.save()
        messages.success(request, 'Sayt dizaynı yeniləndi.')
        return redirect('sites:dashboard', slug=site.slug)
    return render(request, 'sites/edit.html', {'site': site})


@login_required
def sites_delete(request, slug):
    site = get_object_or_404(Site, slug=slug, owner=request.user)
    site.delete()
    messages.success(request, 'Sayt silindi.')
    return redirect('sites:index')


@login_required
def post_create(request, slug):
    site = get_object_or_404(Site, slug=slug, owner=request.user)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if not title:
            messages.error(request, 'Məqalə başlığı daxil edin.')
            return redirect('sites:dashboard', slug=site.slug)
        Post.objects.create(
            site=site,
            title=title,
            content=request.POST.get('content', ''),
            published=request.POST.get('published') == 'on',
        )
        messages.success(request, 'Məqalə yaradıldı.')
        return redirect('sites:dashboard', slug=site.slug)
    return render(request, 'sites/post_form.html', {'site': site, 'post': None})


@login_required
def post_edit(request, slug, post_slug):
    site = get_object_or_404(Site, slug=slug, owner=request.user)
    post = get_object_or_404(Post, site=site, slug=post_slug)
    if request.method == 'POST':
        post.title = request.POST.get('title', '').strip() or post.title
        post.content = request.POST.get('content', '')
        post.published = request.POST.get('published') == 'on'
        post.save()
        messages.success(request, 'Məqalə yeniləndi.')
        return redirect('sites:dashboard', slug=site.slug)
    return render(request, 'sites/post_form.html', {'site': site, 'post': post})


@login_required
def post_delete(request, slug, post_slug):
    site = get_object_or_404(Site, slug=slug, owner=request.user)
    post = get_object_or_404(Post, site=site, slug=post_slug)
    post.delete()
    messages.success(request, 'Məqalə silindi.')
    return redirect('sites:dashboard', slug=site.slug)


def site_public(request, slug):
    site = get_object_or_404(Site, slug=slug)
    posts = site.posts.filter(published=True)
    return render(request, 'sites/public.html', {'site': site, 'posts': posts, 'widgets': site.widgets.all()})


def site_post(request, slug, post_slug):
    site = get_object_or_404(Site, slug=slug)
    post = get_object_or_404(Post, site=site, slug=post_slug, published=True)
    return render(request, 'sites/post.html', {
        'site': site, 'post': post,
        'comments': post.comments.all(),
        'widgets': site.widgets.all(),
    })


def post_comment(request, slug, post_slug):
    site = get_object_or_404(Site, slug=slug)
    post = get_object_or_404(Post, site=site, slug=post_slug, published=True)
    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            if request.user.is_authenticated:
                Comment.objects.create(post=post, author=request.user, body=body)
            else:
                messages.error(request, 'Komment yazmaq üçün daxil olun.')
                return redirect('accounts:login')
    return redirect('sites:post', slug=site.slug, post_slug=post.slug)


@login_required
def widget_create(request, slug):
    site = get_object_or_404(Site, slug=slug, owner=request.user)
    if request.method == 'POST':
        wtype = request.POST.get('type', Widget.TYPE_TEXT)
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        Widget.objects.create(site=site, type=wtype, title=title, content=content)
        messages.success(request, 'Widget əlavə edildi.')
    return redirect('sites:dashboard', slug=site.slug)


@login_required
def widget_delete(request, slug, pk):
    site = get_object_or_404(Site, slug=slug, owner=request.user)
    Widget.objects.filter(pk=pk, site=site).delete()
    messages.success(request, 'Widget silindi.')
    return redirect('sites:dashboard', slug=site.slug)
