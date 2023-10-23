"""Label use cases."""

from functools import partial
from typing import Generator, Literal

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.label import LabelFilters
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.use_cases.base import BaseUseCases
from kili.utils.labels.parsing import parse_labels


class LabelUseCases(BaseUseCases):
    """Label use cases."""

    def count_labels(self, filters: LabelFilters) -> int:
        """Count labels."""
        return self._kili_api_gateway.count_labels(filters=filters)

    def list_labels(
        self,
        project_id: ProjectId,
        filters: LabelFilters,
        fields: ListOrTuple[str],
        options: QueryOptions,
        output_format: Literal["dict", "parsed_label"],
    ) -> Generator:
        """List labels."""
        post_call_function = None

        if output_format == "parsed_label":
            if "jsonResponse" not in fields:
                raise ValueError(
                    "The field 'jsonResponse' is required to parse labels. Please add it to the"
                    " 'fields' argument."
                )

            project = self._kili_api_gateway.get_project(
                project_id, fields=("jsonInterface", "inputType")
            )

            post_call_function = partial(
                parse_labels,
                json_interface=project["jsonInterface"],
                input_type=project["inputType"],
            )

        labels_gen = self._kili_api_gateway.list_labels(
            fields=fields, filters=filters, options=options
        )

        if post_call_function is not None:
            labels_gen = post_call_function(labels=labels_gen)

        return labels_gen
