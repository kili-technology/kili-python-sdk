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

## Transitions

A transition says where an asset goes when a step completes, or when it reaches the end of a group:
to a step, or out of the workflow. The transitions leaving a step are tried by priority, and the
first whose condition holds is taken (`ALWAYS`, `SAMPLE`, `CLASSIFICATION_INCLUDES`,
`ANNOTATION_COUNT_GREATER_THAN`, ...). When none holds, the asset reaches the end of its group,
whose transitions are tried the same way.

A call changes the workflow in one of two modes:

- **Local**, without any transition list (`kili.projects.workflow.steps`, `groups`, and
  `workflow.update` without `create_transitions`, `update_transitions` or `delete_transitions`):
  the server wires each step and group change itself. A new review is sampled after the last step
  of its group, at `sample_percentage`.
- **Explicit**, with a transition list (`kili.projects.workflow.transitions`, and
  `workflow.update` with any of the three lists): the server wires nothing for any change of the
  call. The call gives the transition into each review it creates, the entry and the default
  (`ALWAYS`) transition of each group it creates, and reconnects what followed a step it deletes.
  The SDK sends every transition back with its id, which keeps the outcomes of its samplings, and
  never adds one of its own.

Transitions are saved on projects of the multi-group workflow only. Saving transitions that route
by conditions requires the organization's conditional routing feature (`lab_conditional_routing`);
those keeping a chain of steps per group, such as a `SAMPLE` percentage changed, need nothing.
`kili.projects.workflow.get()` tells whether a project `usesConditionalRouting`, and whether you
`canEditTransitions`. A project that routes by conditions cannot be copied with
`copy_from_project()`.

After a send back, the transitions decide again each time the asset completes a step. With
`workflow.update(keep_path_after_send_back=True)`, an asset sent back goes again through the steps
it went through, whatever its new label, as long as a transition still leads there.

`kili.assets.move_to_next_step(to_step_id=...)` moves assets by hand to any step their transitions
lead to, whatever the conditions of these transitions.

These methods need a version of Kili that serves the conditional routing workflow.

## Moving from the method client

| `kili.client.Kili` | `kili.client_domain.Kili` |
| --- | --- |
| `get_steps` | `kili.projects.workflow.steps.list` |
| `add_review_step` | `kili.projects.workflow.steps.create` |
| `update_labeling_step_properties`, `update_review_step_properties`, `rename_step` | `kili.projects.workflow.steps.update` |
| `delete_last_step` | `kili.projects.workflow.steps.delete` |

What changes on the way:

- `steps.create` takes the review's percentage as `sample_percentage`, which a review requires.
  A review's percentage is then changed with `transitions.update()`, on the `SAMPLE` transition
  leading to it: the domain client has no `step_coverage`, and the `step_coverage` key of
  `workflow.update()` is deprecated.
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

## `kili.projects.workflow.transitions`

::: kili.domain_api.project_workflow.WorkflowTransitionsNamespace
    options:
      filters: ["!^_"]

## Types

::: kili.domain.project.WorkflowStepToCreate

::: kili.domain.project.WorkflowStepGroupToCreate

::: kili.domain.project.WorkflowStepGroupToUpdate

::: kili.domain.project.WorkflowTransitionToCreate

::: kili.domain.project.WorkflowTransitionToUpdate

::: kili.domain.project.WorkflowTransitionCondition
