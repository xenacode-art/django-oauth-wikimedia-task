from rest_framework import serializers
from django.contrib.auth.models import User


class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField()
    edit_count = serializers.IntegerField()
    groups = serializers.ListField(child=serializers.CharField())
    has_oauth = serializers.BooleanField()


class ContributionSerializer(serializers.Serializer):
    title = serializers.CharField()
    timestamp = serializers.DateTimeField()
    comment = serializers.CharField(allow_blank=True)
    size = serializers.IntegerField()


class WikiPageSerializer(serializers.Serializer):
    page_id = serializers.IntegerField()
    page_title = serializers.CharField()
    page_namespace = serializers.IntegerField()
    page_len = serializers.IntegerField()
    page_is_redirect = serializers.BooleanField()


class WikiStatisticsSerializer(serializers.Serializer):
    total_pages = serializers.IntegerField()
    content_pages = serializers.IntegerField()
    redirects = serializers.IntegerField()
    recent_changes_count = serializers.IntegerField()
