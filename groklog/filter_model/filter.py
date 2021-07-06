from dataclasses import dataclass
from typing import Optional

from groklog.process_node import ProcessNode


@dataclass
class Filter:
    filter_name: str
    filter_command: str
    parent: Optional["Filter"]
    process_node: ProcessNode
