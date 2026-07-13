from django import template

register = template.Library()

@register.filter
def trim(value):
    if isinstance(value, str):
        return value.strip()
    return value

@register.filter
def split(value, sep=","):
    if isinstance(value, str):
        return value.split(sep)
    return []