from .fragments import LOCK_FRAGMENT

GQL_DELETE_LOCKS = f'''
mutation($assetID: ID!) {{
  data: deleteLocks(assetID: $assetID) {{
    {LOCK_FRAGMENT}
  }}
}}
'''
