from .fragments import PROJECT_FRAGMENT

GQL_PROJECTS = f'''
query($where: ProjectWhere!, $first: PageSize!, $skip: Int!) {{
  data: projects(where: $where, first: $first, skip: $skip) {{
    {PROJECT_FRAGMENT}
  }}
}}
'''
