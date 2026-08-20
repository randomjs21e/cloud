import json
import mimetypes

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from .models import Album, AlbumPhoto, File, FileVersion, Folder, SharedDrive, SharedDriveFile


IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff', '.ico'}


def _is_image(file_obj):
    if (file_obj.mime_type or '').startswith('image/'):
        return True
    name = (file_obj.name or '').lower()
    return any(name.endswith(ext) for ext in IMAGE_EXTENSIONS)


@login_required
def file_index(request, folder_id=None):
    current = None
    if folder_id:
        current = get_object_or_404(Folder, pk=folder_id, owner=request.user)
    files = File.objects.filter(owner=request.user, is_trashed=False, folder=current)
    folders = Folder.objects.filter(owner=request.user, parent=current)
    all_files = File.objects.filter(owner=request.user, is_trashed=False)
    total_used = sum(f.size for f in all_files)
    limit = request.user.storage_limit_mb * 1024 * 1024
    return render(request, 'files/index.html', {
        'files': files,
        'folders': folders,
        'current': current,
        'breadcrumb': _breadcrumb(current),
        'all_folders': Folder.objects.filter(owner=request.user),
        'total_used': total_used,
        'limit': limit,
        'percent': int((total_used / limit) * 100) if limit else 0,
    })


def _breadcrumb(folder):
    crumbs = []
    cur = folder
    while cur:
        crumbs.append(cur)
        cur = cur.parent
    return list(reversed(crumbs))


@login_required
def folder_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        parent_id = request.POST.get('parent')
        parent = None
        if parent_id:
            parent = get_object_or_404(Folder, pk=parent_id, owner=request.user)
        if not name:
            messages.error(request, 'Qovluq adı daxil edin.')
        else:
            Folder.objects.create(owner=request.user, name=name, parent=parent)
            messages.success(request, f'"{name}" qovluğu yaradıldı.')
        return redirect('files:folder', folder_id=parent.id) if parent else redirect('files:index')
    return redirect('files:index')


@login_required
def folder_delete(request, pk):
    folder = get_object_or_404(Folder, pk=pk, owner=request.user)
    parent = folder.parent
    folder.delete()
    messages.success(request, 'Qovluq silindi.')
    return redirect('files:folder', folder_id=parent.id) if parent else redirect('files:index')


@login_required
def file_move(request, pk):
    f = get_object_or_404(File, pk=pk, owner=request.user)
    folder_id = request.POST.get('folder')
    if folder_id:
        f.folder = get_object_or_404(Folder, pk=folder_id, owner=request.user)
    else:
        f.folder = None
    f.save(update_fields=['folder'])
    messages.success(request, 'Fayl köçürüldü.')
    return redirect('files:folder', folder_id=f.folder.id) if f.folder else redirect('files:index')


@login_required
def file_trash(request, pk):
    f = get_object_or_404(File, pk=pk, owner=request.user)
    f.is_trashed = True
    f.trashed_at = timezone.now()
    f.save(update_fields=['is_trashed', 'trashed_at'])
    messages.success(request, f'{f.name} zibil qutusuna göndərildi.')
    return redirect('files:folder', folder_id=f.folder.id) if f.folder else redirect('files:index')


@login_required
def file_trash_list(request):
    files = File.objects.filter(owner=request.user, is_trashed=True)
    return render(request, 'files/trash.html', {'files': files})


@login_required
def file_restore(request, pk):
    f = get_object_or_404(File, pk=pk, owner=request.user)
    f.is_trashed = False
    f.trashed_at = None
    f.save(update_fields=['is_trashed', 'trashed_at'])
    messages.success(request, f'{f.name} bərpa edildi.')
    return redirect('files:trash')


@login_required
def file_versions(request, pk):
    f = get_object_or_404(File, pk=pk, owner=request.user)
    return render(request, 'files/versions.html', {'file': f, 'versions': f.versions.all()})


@login_required
def file_version_upload(request, pk):
    f = get_object_or_404(File, pk=pk, owner=request.user)
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded = request.FILES['file']
        FileVersion.objects.create(file=f, file_field=uploaded, size=uploaded.size,
                                   note=request.POST.get('note', '').strip())
        messages.success(request, 'Yeni versiya əlavə edildi.')
    return redirect('files:versions', pk=f.id)


@login_required
def file_version_download(request, pk, version_id):
    f = get_object_or_404(File, pk=pk, owner=request.user)
    v = get_object_or_404(FileVersion, pk=version_id, file=f)
    return FileResponse(v.file_field.open('rb'), as_attachment=True, filename=f.name)


@login_required
def photos_index(request):
    photos = [f for f in File.objects.filter(owner=request.user, is_trashed=False) if _is_image(f)]
    albums = Album.objects.filter(owner=request.user)
    return render(request, 'files/photos.html', {'photos': photos, 'albums': albums})


@login_required
def album_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            Album.objects.create(owner=request.user, name=name)
            messages.success(request, f'"{name}" albomu yaradıldı.')
        else:
            messages.error(request, 'Albom adı daxil edin.')
    return redirect('files:photos')


@login_required
def album_detail(request, pk):
    album = get_object_or_404(Album, pk=pk, owner=request.user)
    photos = [ap.file for ap in album.photos.select_related('file')]
    available = [f for f in File.objects.filter(owner=request.user, is_trashed=False) if _is_image(f) and f not in photos]
    return render(request, 'files/album.html', {'album': album, 'photos': photos, 'available': available})


@login_required
def album_add_photo(request, pk):
    album = get_object_or_404(Album, pk=pk, owner=request.user)
    if request.method == 'POST':
        file_id = request.POST.get('file')
        f = get_object_or_404(File, pk=file_id, owner=request.user)
        AlbumPhoto.objects.get_or_create(album=album, file=f)
        messages.success(request, 'Şəkil alboma əlavə edildi.')
    return redirect('files:album', pk=album.id)


@login_required
def album_remove_photo(request, pk, file_id):
    album = get_object_or_404(Album, pk=pk, owner=request.user)
    AlbumPhoto.objects.filter(album=album, file_id=file_id).delete()
    messages.success(request, 'Şəkil albomdan çıxarıldı.')
    return redirect('files:album', pk=album.id)


@login_required
def album_delete(request, pk):
    album = get_object_or_404(Album, pk=pk, owner=request.user)
    album.delete()
    messages.success(request, 'Albom silindi.')
    return redirect('files:photos')


@login_required
def drive_index(request):
    drives = SharedDrive.objects.filter(owner=request.user) | SharedDrive.objects.filter(members=request.user)
    drives = drives.distinct()
    return render(request, 'files/drives.html', {'drives': drives})


@login_required
def drive_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            drive = SharedDrive.objects.create(owner=request.user, name=name)
            drive.members.add(request.user)
            messages.success(request, f'"{name}" sürücüsü yaradıldı.')
            return redirect('files:drive', pk=drive.id)
        messages.error(request, 'Sürücü adı daxil edin.')
    return redirect('files:drives')


@login_required
def drive_detail(request, pk):
    drive = get_object_or_404(SharedDrive, pk=pk)
    if drive.owner != request.user and not drive.members.filter(pk=request.user.pk).exists():
        messages.error(request, 'Bu sürücüyə girişiniz yoxdur.')
        return redirect('files:drives')
    return render(request, 'files/drive.html', {
        'drive': drive,
        'files': drive.files.all(),
        'users': User.objects.exclude(pk=request.user.pk),
    })


@login_required
def drive_add_member(request, pk):
    drive = get_object_or_404(SharedDrive, pk=pk, owner=request.user)
    if request.method == 'POST':
        user_id = request.POST.get('user')
        u = get_object_or_404(User, pk=user_id)
        drive.members.add(u)
        messages.success(request, f'{u.username} sürücüyə əlavə edildi.')
    return redirect('files:drive', pk=drive.id)


@login_required
def drive_remove_member(request, pk, user_id):
    drive = get_object_or_404(SharedDrive, pk=pk, owner=request.user)
    drive.members.remove(user_id)
    messages.success(request, 'Üzv çıxarıldı.')
    return redirect('files:drive', pk=drive.id)


@login_required
def drive_upload(request, pk):
    drive = get_object_or_404(SharedDrive, pk=pk)
    if drive.owner != request.user and not drive.members.filter(pk=request.user.pk).exists():
        messages.error(request, 'Bu sürücüyə girişiniz yoxdur.')
        return redirect('files:drives')
    if request.method == 'POST':
        uploaded = request.FILES.get('file')
        if uploaded:
            import mimetypes
            mime, _ = mimetypes.guess_type(uploaded.name)
            SharedDriveFile.objects.create(
                drive=drive, uploader=request.user, name=uploaded.name,
                file=uploaded, size=uploaded.size, mime_type=mime or 'application/octet-stream',
            )
            messages.success(request, 'Fayl yükləndi.')
        else:
            messages.error(request, 'Fayl seçin.')
    return redirect('files:drive', pk=drive.id)


@login_required
def drive_download(request, pk, file_id):
    drive = get_object_or_404(SharedDrive, pk=pk)
    if drive.owner != request.user and not drive.members.filter(pk=request.user.pk).exists():
        messages.error(request, 'Bu sürücüyə girişiniz yoxdur.')
        return redirect('files:drives')
    f = get_object_or_404(SharedDriveFile, pk=file_id, drive=drive)
    return FileResponse(f.file.open('rb'), as_attachment=True, filename=f.name)


@login_required
def drive_delete_file(request, pk, file_id):
    drive = get_object_or_404(SharedDrive, pk=pk)
    if drive.owner != request.user and not drive.members.filter(pk=request.user.pk).exists():
        messages.error(request, 'Bu sürücüyə girişiniz yoxdur.')
        return redirect('files:drives')
    f = get_object_or_404(SharedDriveFile, pk=file_id, drive=drive)
    if f.file:
        try:
            f.file.close()
        except Exception:
            pass
    try:
        f.file.delete(save=False)
    except Exception:
        pass
    f.delete()
    messages.success(request, 'Fayl silindi.')
    return redirect('files:drive', pk=drive.id)


@login_required
def drive_delete(request, pk):
    drive = get_object_or_404(SharedDrive, pk=pk, owner=request.user)
    drive.delete()
    messages.success(request, 'Sürücü silindi.')
    return redirect('files:drives')


@login_required
def photos_upload(request):
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('file')
        if not uploaded_files:
            messages.error(request, 'Şəkil seçin.')
            return redirect('files:photos')
        files = File.objects.filter(owner=request.user)
        total_used = sum(f.size for f in files)
        limit = request.user.storage_limit_mb * 1024 * 1024
        uploaded_count = 0
        for uploaded in uploaded_files:
            if total_used + uploaded.size > limit:
                messages.error(request, f'{uploaded.name} yüklənmədi: yaddaş limiti doldu.')
                continue
            mime, _ = mimetypes.guess_type(uploaded.name)
            if not (mime or '').startswith('image/'):
                messages.error(request, f'{uploaded.name} şəkil deyil, atlandı.')
                continue
            File.objects.create(
                owner=request.user,
                name=uploaded.name,
                file=uploaded,
                size=uploaded.size,
                mime_type=mime or 'image/jpeg',
            )
            total_used += uploaded.size
            uploaded_count += 1
        if uploaded_count:
            messages.success(request, f'{uploaded_count} şəkil yükləndi.')
    return redirect('files:photos')


@login_required
def file_upload(request):
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('file')
        if not uploaded_files:
            messages.error(request, 'Fayl seçin.')
            return redirect('files:index')
        folder = None
        folder_id = request.POST.get('folder')
        if folder_id:
            folder = get_object_or_404(Folder, pk=folder_id, owner=request.user)
        # When a folder is uploaded, the browser sends the relative paths
        # (e.g. "folder/sub/file.txt") via the folder_paths hidden field.
        folder_paths = []
        raw_paths = request.POST.get('folder_paths', '')
        if raw_paths:
            try:
                folder_paths = json.loads(raw_paths)
            except (ValueError, TypeError):
                folder_paths = []
        files = File.objects.filter(owner=request.user)
        total_used = sum(f.size for f in files)
        limit = request.user.storage_limit_mb * 1024 * 1024
        uploaded_count = 0
        for i, uploaded in enumerate(uploaded_files):
            if total_used + uploaded.size > limit:
                messages.error(request, f'{uploaded.name} yüklənmədi: yaddaş limiti doldu.')
                continue
            # Use the preserved relative path if available, else the base name.
            if i < len(folder_paths) and folder_paths[i]:
                name = folder_paths[i].replace('\\', '/')
            else:
                name = uploaded.name.replace('\\', '/')
            mime, _ = mimetypes.guess_type(name)
            File.objects.create(
                owner=request.user,
                name=name,
                file=uploaded,
                size=uploaded.size,
                mime_type=mime or 'application/octet-stream',
                folder=folder,
            )
            total_used += uploaded.size
            uploaded_count += 1
        if uploaded_count:
            messages.success(request, f'{uploaded_count} fayl yükləndi.')
    if folder:
        return redirect('files:folder', folder_id=folder.id)
    return redirect('files:index')


@login_required
def file_download(request, pk):
    f = get_object_or_404(File, pk=pk, owner=request.user)
    return FileResponse(f.file.open('rb'), as_attachment=True, filename=f.name)


@login_required
def file_delete(request, pk):
    f = get_object_or_404(File, pk=pk, owner=request.user)
    name = f.name
    # Close any open file handle before deleting (Windows requires this)
    if f.file:
        try:
            f.file.close()
        except Exception:
            pass
    # Remove the physical file; on Windows a locked file may fail, so tolerate it
    try:
        f.file.delete(save=False)
    except Exception:
        pass
    f.delete()
    messages.success(request, f'{name} tamamilə silindi.')
    return redirect('files:trash')


@login_required
def file_set_share(request, pk):
    f = get_object_or_404(File, pk=pk, owner=request.user)
    share_type = request.POST.get('share_type', File.SHARE_NONE)
    if share_type not in dict(File.SHARE_CHOICES):
        share_type = File.SHARE_NONE
    f.share_type = share_type
    f.save()
    if share_type == File.SHARE_PUBLIC:
        messages.success(request, 'Hesabsız paylaşım linki aktivləşdirildi.')
    elif share_type == File.SHARE_ACCOUNT:
        messages.success(request, 'Yalnız hesablı istifadəçilər üçün paylaşım aktivləşdirildi.')
    else:
        messages.info(request, 'Paylaşım söndürüldü.')
    return redirect('files:index')


def file_public(request, token):
    f = get_object_or_404(File, share_token=token)
    if f.share_type == File.SHARE_NONE:
        raise Http404('Fayl paylaşılmayıb.')
    # Account-only sharing requires login
    if f.share_type == File.SHARE_ACCOUNT and not request.user.is_authenticated:
        return redirect('{}?next={}'.format(
            reverse('accounts:login'),
            request.path,
        ))
    return render(request, 'files/public.html', {'file': f})


def file_public_download(request, token):
    f = get_object_or_404(File, share_token=token)
    if f.share_type == File.SHARE_NONE:
        raise Http404('Fayl paylaşılmayıb.')
    if f.share_type == File.SHARE_ACCOUNT and not request.user.is_authenticated:
        return redirect('{}?next={}'.format(
            reverse('accounts:login'),
            request.path,
        ))
    return FileResponse(f.file.open('rb'), as_attachment=True, filename=f.name)
