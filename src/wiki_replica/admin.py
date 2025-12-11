"""
Django admin configuration for wiki replica models.

These are read-only admin interfaces for viewing wiki data.
"""

from django.contrib import admin
from .models import Page, Revision, Actor, User, RecentChanges, Logging


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('page_id', 'page_namespace', 'page_title', 'page_is_redirect', 'page_len')
    list_filter = ('page_namespace', 'page_is_redirect', 'page_is_new')
    search_fields = ('page_title',)
    readonly_fields = [f.name for f in Page._meta.fields]

    def has_add_permission(self, request):
        return False  # Read-only

    def has_delete_permission(self, request, obj=None):
        return False  # Read-only


@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    list_display = ('rev_id', 'rev_page', 'rev_timestamp', 'rev_minor_edit', 'rev_len')
    list_filter = ('rev_minor_edit',)
    search_fields = ('rev_id', 'rev_page')
    readonly_fields = [f.name for f in Revision._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('actor_id', 'actor_name', 'actor_user')
    search_fields = ('actor_name',)
    readonly_fields = [f.name for f in Actor._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(User)
class WikiUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'user_name', 'user_editcount', 'user_registration')
    search_fields = ('user_name',)
    readonly_fields = [f.name for f in User._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RecentChanges)
class RecentChangesAdmin(admin.ModelAdmin):
    list_display = ('rc_id', 'rc_timestamp', 'rc_namespace', 'rc_title', 'rc_type', 'rc_bot')
    list_filter = ('rc_type', 'rc_bot', 'rc_minor', 'rc_namespace')
    search_fields = ('rc_title',)
    readonly_fields = [f.name for f in RecentChanges._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Logging)
class LoggingAdmin(admin.ModelAdmin):
    list_display = ('log_id', 'log_type', 'log_action', 'log_timestamp', 'log_namespace', 'log_title')
    list_filter = ('log_type', 'log_action')
    search_fields = ('log_title',)
    readonly_fields = [f.name for f in Logging._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
