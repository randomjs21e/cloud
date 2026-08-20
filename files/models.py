import uuid

from django.conf import settings
from django.db import models


class Folder(models.Model):
    """A user's folder for organizing files (Drive-style)."""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='folders')
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class FileVersion(models.Model):
    """A historical version of a file."""

    file = models.ForeignKey('File', on_delete=models.CASCADE, related_name='versions')
    file_field = models.FileField(upload_to='uploads/%Y/%m/')
    size = models.BigIntegerField(default=0)
    note = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.file.name} v{self.id}'


class File(models.Model):
    """A user's uploaded file."""

    SHARE_NONE = 'none'
    SHARE_PUBLIC = 'public'
    SHARE_ACCOUNT = 'account'
    SHARE_CHOICES = [
        (SHARE_NONE, 'Paylaşılmayıb'),
        (SHARE_PUBLIC, 'Hesabsız (ictimai)'),
        (SHARE_ACCOUNT, 'Yalnız hesablı'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/%Y/%m/')
    size = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    share_type = models.CharField(max_length=10, choices=SHARE_CHOICES, default=SHARE_NONE)
    share_token = models.CharField(max_length=64, unique=True, blank=True)
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True, related_name='files')
    is_trashed = models.BooleanField(default=False)
    trashed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.share_token:
            self.share_token = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def is_office_openable(self):
        """Whether this file can be opened in the Office editor."""
        name = (self.name or '').lower()
        ext = ''
        if '.' in name:
            ext = '.' + name.rsplit('.', 1)[1]
        if ext == '.csv':
            return True
        if (self.mime_type or '').startswith('image/'):
            return True
        return ext in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff', '.ico',
                       '.txt', '.md', '.html', '.htm', '.xml', '.json', '.py', '.js', '.css'}


class Album(models.Model):
    """A photo album (Google Photos-style)."""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='albums')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class AlbumPhoto(models.Model):
    """A photo belonging to an album."""

    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='album_links')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']
        unique_together = ('album', 'file')

    def __str__(self):
        return f'{self.album.name}: {self.file.name}'


class SharedDrive(models.Model):
    """A team shared drive (Google Shared Drive-style)."""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_drives')
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='shared_drives', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SharedDriveFile(models.Model):
    """A file uploaded to a shared drive."""

    drive = models.ForeignKey(SharedDrive, on_delete=models.CASCADE, related_name='files')
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='drive_uploads')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='shared_drives/%Y/%m/')
    size = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
