import functools
import warnings
import base64
import re
import requests
from json import dumps, loads
from types import *


class Compatible():

    def __init__(self, endpoints=['v1']):
        self.endpoints = endpoints
        self.version_extractor = re.compile(r'\/v\d+/')
        self.address_extractor = re.compile(r':400\d+/')

    def client_is_compatible(self, endpoint):
        version_matched = self.version_extractor.search(endpoint)
        address_matched = self.address_extractor.search(endpoint)
        if not version_matched and not address_matched:
            return False
        if address_matched:
            version = 'v1' if address_matched.group() == ':4000/' else 'v2'
        if version_matched:
            version = 'v1' if version_matched.group() == '/v1/' else 'v2'
        return version in self.endpoints

    def __call__(self, resolver, *args, **kwargs):
        @functools.wraps(resolver)
        def checked_resolver(*args, **kwargs):
            try:
                client_endpoint = args[0].auth.client.endpoint
            except:
                raise ValueError(
                    f'Cannot find client endpoint from resolver {resolver.__name__} with arguments {args}')
            if self.client_is_compatible(client_endpoint):
                return resolver(*args, **kwargs)
            else:
                raise EndpointCompatibilityError(
                    resolver.__name__, client_endpoint)
        return checked_resolver


class EndpointCompatibilityError(Exception):
    def __init__(self, resolver, endpoint):
        super().__init__(
            f'Resolver {resolver} is not compatible with the following endpoint : {endpoint}')


class GraphQLError(Exception):
    def __init__(self, mutation, error):
        super().__init__(f'Mutation "{mutation}" failed with error: "{error}"')


def format_result(name, result, Object=None):
    if 'errors' in result:
        raise GraphQLError(name, result['errors'])
    formatted_json = format_json(result['data'][name])
    if Object is None:
        return formatted_json
    if isinstance(formatted_json, list):
        return [Object(element) for element in formatted_json]
    return Object(formatted_json)


def content_escape(content):
    return content.replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"')


def get_data_type(path):
    if re.match(r'.*(jpg|jpeg)$', path.lower()):
        return 'image/png'
    if re.match(r'.*pdf$', path.lower()):
        return 'application/pdf'


def encode_base64(path):
    data_type = get_data_type(path)
    with open(path, 'rb') as image_file:
        return f'data:{data_type};base64,' + \
            base64.b64encode(image_file.read()).decode('ascii')


def is_url(path):
    return isinstance(path, str) and re.match(r'^(http://|https://)', path.lower())


def format_json(result):
    if result is None:
        return result
    if isinstance(result, list):
        return [format_json(elem) for elem in result]
    if isinstance(result, dict):
        for key, value in result.items():
            if key in ['jsonInterface', 'jsonMetadata', 'jsonResponse']:
                if (value == '' or value is None) and not (is_url(value) and key == 'jsonInterface'):
                    result[key] = dict()
                else:
                    try:
                        if is_url(value):
                            result[key] = requests.get(value).json()
                        else:
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


def format_metadata(metadata):
    if metadata is None:
        return metadata
    elif isinstance(metadata, str):
        return metadata
    elif isinstance(metadata, dict) or isinstance(metadata, list):
        return dumps(metadata)
    else:
        raise Exception(
            f"Metadata {metadata} of type {type(metadata)} must either be None, a string a list or a dict.")


def convert_to_list_of_none(array, length):
    if isinstance(array, list):
        if len(array) != length:
            raise Exception(f'array should have length {length}')
        else:
            return array
    else:
        return [None] * length


def is_none_or_empty(object):
    object_is_empty = isinstance(object, list) and len(object) == 0
    return object is None or object_is_empty


def list_is_not_none_else_none(object):
    return [object] if object is not None else None


def infer_id_from_external_id(playground, asset_id: str, external_id: str, project_id: str):
    if asset_id is None and external_id is None:
        raise Exception(
            'Either provide asset_id or external_id and project_id')
    if asset_id is not None:
        return asset_id
    assets = playground.assets(
        external_id_contains=[external_id], project_id=project_id, fields=['id'], disable_tqdm=True)
    if len(assets) == 0:
        raise Exception(
            f'No asset found with external ID "{external_id}"')
    if len(assets) > 1:
        raise Exception(
            f'Several assets found containing external ID "{external_id}": {assets}. Please, use asset ID instead.')
    return assets[0]['id']
