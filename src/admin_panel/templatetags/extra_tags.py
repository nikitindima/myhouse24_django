from django import template

register = template.Library()


@register.filter(name='get_int')
def get_int(value):
    """Removes all values of arg from the given string"""
    return value.split('-')[1]
