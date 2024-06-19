from django import template

register = template.Library()

@register.filter(name='dict_get')
def dict_get(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, 0)
    return 0



# @register.filter(name='get_shredd')
# def get_shredd(dictionary, key):
#     if isinstance(dictionary, dict):
#         return dictionary.get(key, 0)
#     return 0