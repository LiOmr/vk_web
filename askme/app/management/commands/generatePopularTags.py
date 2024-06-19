from django.core.management.base import BaseCommand
from django.core.cache import cache
from app.models import *


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        popularTags = Tag.objects.get_hot_tags()
        cache.set('popular_users', popularTags, 12 * 60 * 60)
