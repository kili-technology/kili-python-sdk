from json import dumps
from typing import List

from ..helpers import format_result


def count_assets(client, project_id: str,
                 external_id_contains: List[str] = None,
                 status_in: List[str] = None,
                 author_in: List[str] = None,
                 consensus_mark_gt: float = None,
                 consensus_mark_lt: float = None,
                 honeypot_mark_gt: float = None,
                 honeypot_mark_lt: float = None,
                 skipped: bool = None,
                 label_external_id_contains: str = None,
                 label_type_in: List[str] = None,
                 label_status_in: List[str] = None,
                 label_author_in: List[str] = None,
                 label_consensus_mark_gt: float = None,
                 label_consensus_mark_lt: float = None,
                 label_honeypot_mark_gt: float = None,
                 label_honeypot_mark_lt: float = None,
                 label_created_at_gt: float = None,
                 label_created_at_lt: float = None,
                 label_skipped: bool = None):
    formatted_external_id_contains = dumps(
        []) if external_id_contains is None else dumps(external_id_contains)
    formatted_status_in = dumps([]) if status_in is None else dumps(status_in)
    formatted_author_in = dumps([]) if author_in is None else dumps(author_in)
    formatted_consensus_mark_gt = 'null' if consensus_mark_gt is None else f'{consensus_mark_gt}'
    formatted_consensus_mark_lt = 'null' if consensus_mark_lt is None else f'{consensus_mark_lt}'
    formatted_honeypot_mark_gt = 'null' if honeypot_mark_gt is None else f'{honeypot_mark_gt}'
    formatted_honeypot_mark_lt = 'null' if honeypot_mark_lt is None else f'{honeypot_mark_lt}'
    formatted_skipped = 'null' if skipped is None else f'{skipped}'.lower()
    formatted_label_external_id_contains = dumps(
        []) if label_external_id_contains is None else dumps(label_external_id_contains)
    formatted_label_type_in = dumps(
        []) if label_type_in is None else dumps(label_type_in)
    formatted_label_status_in = dumps(
        []) if label_status_in is None else dumps(label_status_in)
    formatted_label_author_in = dumps(
        []) if label_author_in is None else dumps(label_author_in)
    formatted_label_consensus_mark_gt = 'null' if label_consensus_mark_gt is None else f'{label_consensus_mark_gt}'
    formatted_label_consensus_mark_lt = 'null' if label_consensus_mark_lt is None else f'{label_consensus_mark_lt}'
    formatted_label_honeypot_mark_gt = 'null' if label_honeypot_mark_gt is None else f'{label_honeypot_mark_gt}'
    formatted_label_honeypot_mark_lt = 'null' if label_honeypot_mark_lt is None else f'{label_honeypot_mark_lt}'
    formatted_label_created_at_gt = 'null' if label_created_at_gt is None else f'"{label_created_at_gt}"'
    formatted_label_created_at_lt = 'null' if label_created_at_lt is None else f'"{label_created_at_lt}"'
    formatted_label_skipped = 'null' if label_skipped is None else f'{label_skipped}'.lower(
    )

    result = client.execute('''
            query {
              countAssetsWithSearch(projectID: "%s"
                assetsWhere: {
                  externalIdIn: %s
                  statusIn: %s
                  authorIn: %s
                  consensusMarkGte: %s
                  consensusMarkLte: %s
                  honeypotMarkGte: %s
                  honeypotMarkLte: %s
                  skipped: %s
                }
                labelsWhere: {
                  externalIdIn: %s
                  typeIn: %s
                  statusIn: %s
                  authorIn: %s
                  consensusMarkGte: %s
                  consensusMarkLte: %s
                  honeypotMarkGte: %s
                  honeypotMarkLte: %s
                  createdAtGte: %s
                  createdAtLte: %s
                  skipped: %s
                })
            }
            ''' % (project_id,
                   formatted_external_id_contains,
                   formatted_status_in,
                   formatted_author_in,
                   formatted_consensus_mark_gt,
                   formatted_consensus_mark_lt,
                   formatted_honeypot_mark_gt,
                   formatted_honeypot_mark_lt,
                   formatted_skipped,
                   formatted_label_external_id_contains,
                   formatted_label_type_in,
                   formatted_label_status_in,
                   formatted_label_author_in,
                   formatted_label_consensus_mark_gt,
                   formatted_label_consensus_mark_lt,
                   formatted_label_honeypot_mark_gt,
                   formatted_label_honeypot_mark_lt,
                   formatted_label_created_at_gt,
                   formatted_label_created_at_lt,
                   formatted_label_skipped))
    count = format_result('countAssetsWithSearch', result)
    return count
