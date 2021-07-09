from dataclasses import dataclass, field
from typing import List

from groklog.process_node import ProcessNode


@dataclass
class Filter:
    name: str
    command: str
    process_node: ProcessNode
    children: List["Filter"] = field(default_factory=list)

    def add_child(self, filter: "Filter"):
        """Adds and subscribes the child"""
        self.process_node.subscribe(
            ProcessNode.Topic.BYTES_DATA_STREAM, filter.process_node.write
        )
        self.children.append(filter)

    def close(self, timeout=None):
        self.process_node.close(timeout=timeout)
        for child in self.children:
            child.close(timeout=timeout)
