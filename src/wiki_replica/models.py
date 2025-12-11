"""
Django ORM models for MediaWiki database replica tables.

These models provide read-only access to MediaWiki database replicas
available on Toolforge. They map to the actual MediaWiki database schema.

Note: These are managed=False models, meaning Django won't create/modify
the tables. They're read-only representations of existing wiki tables.
"""

from django.db import models


class Page(models.Model):
    """
    Represents the MediaWiki 'page' table.
    Contains metadata for all pages in the wiki.
    """
    page_id = models.AutoField(primary_key=True)
    page_namespace = models.IntegerField()
    page_title = models.CharField(max_length=255)
    page_is_redirect = models.BooleanField(default=False)
    page_is_new = models.BooleanField(default=False)
    page_random = models.FloatField()
    page_touched = models.CharField(max_length=14)
    page_links_updated = models.CharField(max_length=14, null=True, blank=True)
    page_latest = models.IntegerField()
    page_len = models.IntegerField()
    page_content_model = models.CharField(max_length=32, null=True, blank=True)
    page_lang = models.CharField(max_length=35, null=True, blank=True)

    class Meta:
        managed = False  # Don't let Django manage this table
        db_table = 'page'  # Use existing wiki table
        app_label = 'wiki_replica'

    def __str__(self):
        return f"{self.page_namespace}:{self.page_title}"


class Revision(models.Model):
    """
    Represents the MediaWiki 'revision' table.
    Contains all revisions made to wiki pages.
    """
    rev_id = models.AutoField(primary_key=True)
    rev_page = models.IntegerField()
    rev_comment_id = models.BigIntegerField()
    rev_actor = models.BigIntegerField()
    rev_timestamp = models.CharField(max_length=14)
    rev_minor_edit = models.BooleanField(default=False)
    rev_deleted = models.SmallIntegerField(default=0)
    rev_len = models.IntegerField(null=True, blank=True)
    rev_parent_id = models.IntegerField(null=True, blank=True)
    rev_sha1 = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = 'revision'
        app_label = 'wiki_replica'

    def __str__(self):
        return f"Revision {self.rev_id}"


class Actor(models.Model):
    """
    Represents the MediaWiki 'actor' table.
    Maps user/IP actors to revision and logging data.
    """
    actor_id = models.BigAutoField(primary_key=True)
    actor_user = models.IntegerField(null=True, blank=True)
    actor_name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'actor'
        app_label = 'wiki_replica'

    def __str__(self):
        return self.actor_name


class User(models.Model):
    """
    Represents the MediaWiki 'user' table.
    Contains information about registered users.
    """
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=255, unique=True)
    user_real_name = models.CharField(max_length=255, blank=True)
    user_email = models.CharField(max_length=255, blank=True)
    user_touched = models.CharField(max_length=14)
    user_token = models.CharField(max_length=32)
    user_email_authenticated = models.CharField(max_length=14, null=True, blank=True)
    user_email_token = models.CharField(max_length=32, null=True, blank=True)
    user_email_token_expires = models.CharField(max_length=14, null=True, blank=True)
    user_registration = models.CharField(max_length=14, null=True, blank=True)
    user_editcount = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'user'
        app_label = 'wiki_replica'

    def __str__(self):
        return self.user_name


class Logging(models.Model):
    """
    Represents the MediaWiki 'logging' table.
    Contains log entries for various wiki actions.
    """
    log_id = models.AutoField(primary_key=True)
    log_type = models.CharField(max_length=32)
    log_action = models.CharField(max_length=32)
    log_timestamp = models.CharField(max_length=14)
    log_actor = models.BigIntegerField()
    log_namespace = models.IntegerField()
    log_title = models.CharField(max_length=255)
    log_page = models.IntegerField(null=True, blank=True)
    log_comment_id = models.BigIntegerField()
    log_params = models.TextField()
    log_deleted = models.SmallIntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'logging'
        app_label = 'wiki_replica'

    def __str__(self):
        return f"{self.log_type}:{self.log_action} - {self.log_id}"


class RecentChanges(models.Model):
    """
    Represents the MediaWiki 'recentchanges' table.
    Contains recent changes to the wiki (rolling window).
    """
    rc_id = models.AutoField(primary_key=True)
    rc_timestamp = models.CharField(max_length=14)
    rc_actor = models.BigIntegerField()
    rc_namespace = models.IntegerField()
    rc_title = models.CharField(max_length=255)
    rc_comment_id = models.BigIntegerField()
    rc_minor = models.BooleanField(default=False)
    rc_bot = models.BooleanField(default=False)
    rc_new = models.BooleanField(default=False)
    rc_cur_id = models.IntegerField()
    rc_this_oldid = models.IntegerField()
    rc_last_oldid = models.IntegerField()
    rc_type = models.SmallIntegerField()
    rc_source = models.CharField(max_length=16)
    rc_patrolled = models.SmallIntegerField(default=0)
    rc_ip = models.CharField(max_length=40, blank=True)
    rc_old_len = models.IntegerField(null=True, blank=True)
    rc_new_len = models.IntegerField(null=True, blank=True)
    rc_deleted = models.SmallIntegerField(default=0)
    rc_logid = models.IntegerField(default=0)
    rc_log_type = models.CharField(max_length=255, null=True, blank=True)
    rc_log_action = models.CharField(max_length=255, null=True, blank=True)
    rc_params = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'recentchanges'
        app_label = 'wiki_replica'

    def __str__(self):
        return f"RC {self.rc_id}: {self.rc_namespace}:{self.rc_title}"
