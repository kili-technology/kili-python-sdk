def kili_append_to_dataset(client, project_id, content, external_id, filename, is_instructions,
                           instructions, is_honeypot, consensus_mark, honeypot_mark, status):
    result = client.execute('''
    mutation {
      appendToDataset(projectID: "%s"
        content: "%s",
        externalID: "%s",
        filename: "%s",
        isInstructions: %s,
        instructions: "%s",
        isHoneypot: %s,
        consensusMark: %d,
        honeypotMark: %d,
        status: %s) {
        id
      }
    }
    ''' % (project_id, content, external_id, filename, str(is_instructions).lower(),
           instructions, str(is_honeypot).lower(), consensus_mark, honeypot_mark, status))
    return loads(result)['data']['appendToDataset']

