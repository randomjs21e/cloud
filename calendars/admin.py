from django.contrib import admin

from .models import Event, Invitation, Notification


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'date', 'time')
    list_filter = ('owner', 'date')


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('event', 'invitee', 'status')
    list_filter = ('status',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'text', 'is_read', 'created_at')
    list_filter = ('is_read',)
