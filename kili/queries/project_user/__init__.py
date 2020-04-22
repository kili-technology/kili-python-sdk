from ...helpers import format_result
from .queries import GQL_PROJECT_USERS, GQL_PROJECT_USERS_WITH_KPIS


def project_users(client, email=None, id=None, organization_id=None, project_id=None, first=100, skip=0, with_kpis=False):
    variables = {
        'first': first,
        'skip': skip,
        'where': {
            'id': id,
            'project': {
                'id': project_id,
            },
            'user': {
                'email': email,
                'organizationId': organization_id,
            },
        }
    }
    query = GQL_PROJECT_USERS_WITH_KPIS if with_kpis else GQL_PROJECT_USERS
    result = client.execute(query, variables)
    return format_result('data', result)
