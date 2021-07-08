from dataclasses import dataclass
from typing import Optional

from groklog.process_node import ProcessNode


@dataclass
class Filter:
    name: str
    command: str
    parent: Optional["Filter"]
    process_node: ProcessNode
