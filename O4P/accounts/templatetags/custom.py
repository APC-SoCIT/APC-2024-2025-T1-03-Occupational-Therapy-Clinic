from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    """Adds the specified class to the form field's widget."""
    return value.as_widget(attrs={'class': arg})