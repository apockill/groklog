from pathlib import Path
from typing import Dict, Optional

from groklog.filter_manager import Filter, exceptions
from groklog.process_node import GenericProcessIO, ProcessNode, ShellProcessIO

ROOT_FILTER_NAME = "Shell"
"""The default name for the root shell process"""


class FilterManager:
    """
    This class handles the storing, saving, loading, and creation of ProcessNode objects
    """

    # Set constants for how serialization. The UI also uses these for labels.
    FILTER_PARENT = "parent_process"
    FILTER_NAME = "name"
    FILTER_COMMAND = "command"

    def __init__(self, shell: ShellProcessIO):
        """
        :param shell: The shell, which will be the 'root' process for input
        """

        self._filters: Dict[str, Filter] = {}
        """A dictionary of Filter.name: Filter"""

        # Register the "root" filter
        self._filters[ROOT_FILTER_NAME] = Filter(
            name=ROOT_FILTER_NAME,
            command="",
            process_node=shell,
        )

    def __iter__(self):
        for filter in self._filters.values():
            yield filter

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
        parent: Filter,
        process_node: ProcessNode = None,
    ) -> Filter:
        """Create and register a new filter.
        :param name: The name of the filter
        :param command: The shell command to run
        :param parent: The children process to feed results into the new filter
        :param process_node: The process node to subscribe to the parent
        :return: The new filter
        """

        if name in self._filters:
            raise exceptions.DuplicateFilterError(
                f"A filter with name '{name}' already exists!"
            )

        # Create and register the filter
        filter = Filter(
            name=name,
            command=command,
            process_node=process_node,
        )
        parent.add_child(filter)
        self._filters[name] = filter
        return filter
