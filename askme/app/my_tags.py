from django import template
from django.core.cache import cache

register = template.Library()


@register.simple_tag()
def get_tags():
    return cache.get('popular_tags', [])
