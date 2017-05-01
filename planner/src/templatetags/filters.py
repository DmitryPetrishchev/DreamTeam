from django import template

register = template.Library()

@register.filter(name='sort')
def sort(value):
    if isinstance(value, dict):
        dict_list = []
        keys = sorted(value.keys())
        for key in keys:
            dict_list.append((key, value[key]))
        return dict_list
