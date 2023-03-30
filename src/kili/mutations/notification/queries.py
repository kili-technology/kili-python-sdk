"""Queries of notification mutations."""

from .fragments import NOTIFICATION_FRAGMENT

GQL_CREATE_NOTIFICATION = f"""
mutation(
    $data: NotificationData!
) {{
  data: createNotification(
    data: $data
  ) {{
    {NOTIFICATION_FRAGMENT}
  }}
}}
"""

GQL_UPDATE_PROPERTIES_IN_NOTIFICATION = f"""
mutation(
    $id: ID!
    $hasBeenSeen: Boolean
    $status: NotificationStatus
    $url: String
) {{
  data: updatePropertiesInNotification(
    where: {{id: $id}}
    data: {{
      hasBeenSeen: $hasBeenSeen
      status: $status
      url: $url
    }}
  ) {{
    {NOTIFICATION_FRAGMENT}
  }}
}}
"""
