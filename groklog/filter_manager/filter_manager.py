import json
from pathlib import Path
from typing import Dict, Iterator

from groklog.filter_manager import exceptions
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
    FILTER_CHILDREN = "children"

    def __init__(self, shell: ShellProcessIO):
        """
        :param shell: The shell, which will be the 'root' process for input
        """
        self.selected_filter = shell

        self._filters: Dict[str, Filter] = {}
        """A dictionary of Filter.name: Filter"""

        # Register the "root" filter
        self._filters[ROOT_FILTER_NAME] = shell

    def __iter__(self) -> Iterator[ProcessNode]:
        for filter in self._filters.values():
            yield filter

    @property
    def root_filter(self) -> ShellProcessIO:
        return self.get_filter(ROOT_FILTER_NAME)

    def get_filter(self, filter_name: str) -> ProcessNode:
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
        parent: ProcessNode,
    ) -> ProcessNode:
        """Create and register a new filter.
        :param name: The name of the filter
        :param command: The shell command to run
        :param parent: The children process to feed results into the new filter
        :return: The new filter
        """

        if name in self._filters:
            raise exceptions.DuplicateFilterError(
                f"A filter with name '{name}' already exists!"
            )

        # Create and register the filter
        filter = GenericProcessIO(
            name=name,
            command=command,
        )
        parent.add_child(filter)
        self._filters[name] = filter
        return filter

    def save_profile(self, profile_path: Path):
        def serialize_process_node(process_node: ProcessNode):
            return {
                self.FILTER_NAME: process_node.name,
                self.FILTER_COMMAND: process_node.command,
                self.FILTER_CHILDREN: [
                    serialize_process_node(c) for c in process_node.children
                ],
            }

        profile_path.parent.mkdir(parents=True, exist_ok=True)
        with profile_path.open("w") as file:
            json.dump(serialize_process_node(self.root_filter), file)

    def load_profile(self, profile_path: Path):
        def deserialize_process_node(node_info, parent=None):
            if parent is None:
                node = self.root_filter
            else:
                node = self.create_filter(
                    name=node_info[self.FILTER_NAME],
                    command=node_info[self.FILTER_COMMAND],
                    parent=parent,
                )

            for child_info in node_info[self.FILTER_CHILDREN]:
                deserialize_process_node(child_info, parent=node)
            return node

        with profile_path.open("r") as file:
            profile_json = json.load(file)
        deserialize_process_node(profile_json)

    def close(self):
        self.root_filter.close()
