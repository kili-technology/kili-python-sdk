"""GraphQL Project Workflow operations."""


def get_update_project_workflow_mutation(fragment: str) -> str:
    """Return the GraphQL editProjectWorkflowSettings mutation."""
    return f"""
        mutation editProjectWorkflowSettings($input: EditProjectWorkflowSettingsInput!) {{
            data: editProjectWorkflowSettings(input: $input) {{
                {fragment}
            }}
        }}
        """
