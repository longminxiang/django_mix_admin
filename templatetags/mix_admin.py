import json
from django.template import Library
from django.utils.html import _json_script_escapes

register = Library()


@register.filter
def get_item(dic, key):
    return dic.get(key)


@register.filter
def json_str(value):
    from django.core.serializers.json import DjangoJSONEncoder
    json_str = json.dumps(value, cls=DjangoJSONEncoder).translate(_json_script_escapes).replace('"', "'")
    return json_str


@register.filter
def json_str1(value):
    from django.core.serializers.json import DjangoJSONEncoder
    json_str = json.dumps(value, cls=DjangoJSONEncoder).translate(_json_script_escapes)
    return json_str
