from .fragments import LABEL_FRAGMENT

GQL_LABELS = f'''
query ($where: LabelWhere!, $first: PageSize!, $skip: Int!) {{
  data: labels(where: $where, first: $first, skip: $skip) {{
    {LABEL_FRAGMENT}
  }}
}}
'''
