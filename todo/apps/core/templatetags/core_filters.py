from django import template
from django.utils.timezone import now

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_count(dictionary, key):
    return len(dictionary.get(key))


@register.filter
def days_left(d):
    return (d - now().date()).days
