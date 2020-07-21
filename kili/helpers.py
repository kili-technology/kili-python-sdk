import functools
import warnings
import base64
import re
from json import dumps, loads
from types import *


class GraphQLError(Exception):
    def __init__(self, mutation, error):
        super().__init__(f'Mutation "{mutation}" failed with error: "{error}"')


def format_result(name, result):
    if 'errors' in result:
        raise GraphQLError(name, result['errors'])
    return format_json(result['data'][name])


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


def format_json(result):
    if result is None:
        return result
    if isinstance(result, list):
        return [format_json(elem) for elem in result]
    if isinstance(result, dict):
        for key, value in result.items():
            if key in ['jsonInterface', 'jsonMetadata', 'jsonResponse']:
                if value == '' or value is None:
                    result[key] = dict()
                else:
                    try:
                        result[key] = loads(value)
                    except:
                        raise ValueError(
                            'Json Metadata / json response / json interface should be valid jsons')
            else:
                result[key] = format_json(value)
        return result
    return result


def fragment_builder(fields, type_of_fields):
    fragment = ''
    subfields = [field.split('.', 1) for field in fields if '.' in field]
    if subfields:
        for subquery in set([subfield[0] for subfield in subfields]):
            type_of_fields_subquery = getattr(type_of_fields, subquery)
            try:
                if issubclass(type_of_fields_subquery, object):
                    fields_subquery = [subfield[1]
                                       for subfield in subfields if subfield[0] == subquery]
                    fragment += f' {subquery}{{{fragment_builder(fields_subquery,type_of_fields_subquery)}}}'
            except ValueError:
                print(f'{subquery} must be a valid subquery field')
        fields = [field for field in fields if '.' not in field]
    for field in fields:
        try:
            getattr(type_of_fields, field)
        except ValueError:
            print(f'{field} must be an instance of {type_of_fields}')
        if isinstance(field, str):
            fragment += f' {field}'
        else:
            raise Exception('Please provide the fields to query as strings')
    return fragment


def deprecate(msg, type=DeprecationWarning):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(msg, type, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator
