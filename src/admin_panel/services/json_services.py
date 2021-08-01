import json

from django.core.serializers.json import DjangoJSONEncoder


def dump_to_json_or_none(qs):
    if qs.exists():
        result = json.dumps(list(qs), cls=DjangoJSONEncoder)
    else:
        result = None
    return result
