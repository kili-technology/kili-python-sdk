import base64
import re
from json import dumps, loads


class GraphQLError(Exception):
    def __init__(self, mutation, error):
        super().__init__(f'Mutation "{mutation}" failed with error: "{error}"')


def format_result(name, result):
    if 'errors' in result:
        raise GraphQLError(name, result['errors'])
    return result['data'][name]


def json_escape(dict):
    str = dumps(dict)
    return dumps(str)[1:-1]


def content_escape(content):
    return content.replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"')


def get_data_type(path):
    if re.match(r'(jpg|jpeg)$', path.lower()):
        return 'image/png'


def encode_image(path):
    data_type = get_data_type(path)
    with open(path, 'rb') as image_file:
        return f'data:{data_type};base64,' + \
            base64.b64encode(image_file.read()).decode('ascii')


def is_url(path):
    return re.match(r'^(http://|https://)', path.lower())
