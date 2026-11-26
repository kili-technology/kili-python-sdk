# Project Workflow (domain client)

The workflow of a project is reached as `kili.projects.workflow` on the domain client:

```python
from kili.client_domain import Kili

kili = Kili()
kili.projects.workflow.steps.list(project_id="my_project")
```

A step is given by its id, by its name when no other step of the project has it, or as
`{"name": ..., "group_name": ...}`. A step group is given by its id or its name. Step groups only
exist in the multi-group workflow.

## Moving from the method client

| `kili.client.Kili` | `kili.client_domain.Kili` |
| --- | --- |
| `get_steps` | `kili.projects.workflow.steps.list` |
| `add_review_step` | `kili.projects.workflow.steps.create` |
| `update_labeling_step_properties`, `update_review_step_properties`, `rename_step` | `kili.projects.workflow.steps.update` |
| `delete_last_step` | `kili.projects.workflow.steps.delete` |

What changes on the way:

- `steps.create` takes the review's percentage as `sample_percentage`, which a review requires.
- `steps.update` changes every property of a step in one call, and refuses one that does not fit
  the step's type. It changes no assignees: `add_reviewers`, `add_labelers` and their `remove_`
  pairs do.
- `steps.delete` deletes any step, not only the last one.

## `kili.projects.workflow`

::: kili.domain_api.project_workflow.WorkflowNamespace
    options:
      filters: ["!^_"]

## `kili.projects.workflow.steps`

::: kili.domain_api.project_workflow.WorkflowStepsNamespace
    options:
      filters: ["!^_"]

## `kili.projects.workflow.groups`

::: kili.domain_api.project_workflow.WorkflowGroupsNamespace
    options:
      filters: ["!^_"]

## Types

::: kili.domain.project.WorkflowStepToCreate

::: kili.domain.project.WorkflowStepGroupToCreate

::: kili.domain.project.WorkflowStepGroupToUpdate
