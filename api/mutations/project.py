def update_properties_in_project(client, project_id, min_consensus_size=None, consensus_tot_coverage=None):
    formatted_min_consensus_size = 'null' if min_consensus_size is None else int(min_consensus_size)
    formatted_consensus_tot_coverage = 'null' if consensus_tot_coverage is None else int(consensus_tot_coverage)

    result = client.execute('''
        mutation {
          updatePropertiesInProject(
            where: {id: "%s"},
            data: {
              minConsensusSize: %s
              consensusTotCoverage: %s
            }
          ) {
            id
          }
        }
        ''' % (project_id, formatted_min_consensus_size, formatted_consensus_tot_coverage))
    return loads(result)['data']['updatePropertiesInProject']

