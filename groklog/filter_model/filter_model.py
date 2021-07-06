from typing import Dict, Optional

from groklog.filter_model import Filter, exceptions
from groklog.process_node import ProcessNode, ShellProcessIO

ROOT_FILTER_NAME = "Shell"
"""The default name for the root shell process"""


class FilterModel:
    # Set constants for how serialization and UI will map data
    FILTER_NAME = "filter_name"
    FILTER_COMMAND = "filter_command"

    def __init__(self, shell: ShellProcessIO):
        self._filters: Dict[str, Filter] = {}
        """A dictionary of filter_name: Filter"""

        # Register the "root" filter
        self.create_filter(
            name=ROOT_FILTER_NAME, command="", parent=None, process_node=shell
        )

    @property
    def root_filter(self) -> Filter:
        return self.get_filter(ROOT_FILTER_NAME)

    def get_filter(self, filter_name: str) -> Filter:
        try:
            return self._filters[filter_name]
        except KeyError:
            raise exceptions.FilterNotFoundError(
                f"Could not find a filter of name {filter_name}"
            )

    def create_filter(
        self,
        name: str,
        command: str,
        parent: Optional[Filter],
        process_node: ProcessNode = None,
    ) -> Filter:
        if parent is None and not isinstance(process_node, ShellProcessIO):
            raise RuntimeError("The root filter must be of type ShellProcessIO")

        if name in self._filters:
            raise exceptions.DuplicateFilterError(
                f"A filter with name '{name}' already exists!"
            )

        # Create and register the filter
        filter = Filter(
            filter_name=name,
            filter_command=command,
            parent=parent,
            process_node=process_node,
        )
        self._filters[name] = filter
        return filter
