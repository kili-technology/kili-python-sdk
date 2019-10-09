from json import loads, dumps


class GraphQLError(Exception):
    def __init__(self, mutation, error):
        super().__init__(f'Mutation "{mutation}" failed with error: "{error}"')


def format_result(name, result):
    json_result = loads(result)
    if 'errors' in json_result:
        raise GraphQLError(name, json_result['errors'])

    return json_result['data'][name]


def json_escape(dict):
    str = dumps(dict)
    return str.replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\\$', "$")
