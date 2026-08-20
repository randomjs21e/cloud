from django.contrib import admin

from .models import ChatGroup, Membership, Message


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0


@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    inlines = [MembershipInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('group', 'author', 'body', 'created_at')
    list_filter = ('group',)
