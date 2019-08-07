from json import loads


def update_consensus_in_many_assets(client, asset_ids, consensus_marks, are_used_for_consensus):
    asset_ids_in_string = '", "'.join(asset_ids)
    are_used_for_consensus_in_string = ', '.join(
        [str(is_used_for_consensus).lower() for is_used_for_consensus in are_used_for_consensus])
    result = client.execute('''
        mutation {
          updateConsensusInManyAssets(
            assetIDs: ["%s"],
            consensusMarks: %s
            areUsedForConsensus: [%s]
          ) {
              id
              consensusMark
              isUsedForConsensus
          }
        }
        ''' % (asset_ids_in_string, consensus_marks, are_used_for_consensus_in_string))
    return loads(result)['data']['updateConsensusInManyAssets']
