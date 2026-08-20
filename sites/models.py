from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Site(models.Model):
    """A user's public website (WordPress-style)."""

    THEME_LIGHT = 'light'
    THEME_DARK = 'dark'
    THEME_BRAND = 'brand'
    THEME_SUNSET = 'sunset'
    THEME_FOREST = 'forest'
    THEME_CHOICES = [
        (THEME_LIGHT, 'Açıq'),
        (THEME_DARK, 'Tünd'),
        (THEME_BRAND, 'Mavi'),
        (THEME_SUNSET, 'Gün batımı'),
        (THEME_FOREST, 'Meşə'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sites')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255, blank=True, default='')
    tagline = models.CharField(max_length=255, blank=True, default='')
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default=THEME_LIGHT)
    ad_code = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or 'site'
            slug = base
            n = 1
            while Site.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f'{base}-{n}'
            self.slug = slug
        if not self.title:
            self.title = self.name
        super().save(*args, **kwargs)


class Post(models.Model):
    """A blog post on a site."""

    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    content = models.TextField(blank=True, default='')
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('site', 'slug')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or 'post'
            slug = base
            n = 1
            while Post.objects.filter(site=self.site, slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f'{base}-{n}'
            self.slug = slug
        super().save(*args, **kwargs)


class Comment(models.Model):
    """A comment on a blog post."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='site_comments')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author.username}: {self.body[:40]}'


class Widget(models.Model):
    """A configurable widget shown on a site's sidebar (WordPress-style)."""

    TYPE_ABOUT = 'about'
    TYPE_LINKS = 'links'
    TYPE_TEXT = 'text'
    TYPE_RECENT = 'recent'
    TYPE_CHOICES = [
        (TYPE_ABOUT, 'Haqqında'),
        (TYPE_LINKS, 'Linklər'),
        (TYPE_TEXT, 'Mətn'),
        (TYPE_RECENT, 'Son məqalələr'),
    ]

    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='widgets')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_TEXT)
    title = models.CharField(max_length=255, blank=True, default='')
    content = models.TextField(blank=True, default='')
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ['position', 'id']

    def __str__(self):
        return f'{self.site.name}: {self.get_type_display()}'
