LOCK_FRAGMENT = '''
id
author {
  email
}
createdAt
lockType
'''

ASSET_FRAGMENT_AUTHOR = '''
id
email
'''

ASSET_FRAGMENT = f'''
id
externalId
content
isHoneypot
duration
consensusMark
honeypotMark
status
isUsedForConsensus
jsonMetadata
priority
labels {{
  id
  createdAt
  labelType
  jsonResponse
  isLatestLabelForUser
  numberOfAnnotations
  secondsToLabel
  totalSecondsToLabel
  honeypotMark
  skipped
  author {{
    {ASSET_FRAGMENT_AUTHOR}
  }}
}}
locks {{
  {LOCK_FRAGMENT}
}}
'''
