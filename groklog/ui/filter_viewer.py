from threading import RLock
from typing import Any

from rich.console import Console
from rich.text import Text
from textual import events
from textual.widgets import ScrollView

from groklog.process_node import ProcessNode, ShellProcessIO


class FilterViewer(ScrollView):
    def __init__(self, *args: Any, process_node: ProcessNode, **kwargs: Any):
        super().__init__(*args, fluid=False, **kwargs)
        self._process_node = process_node
        self._process_node.subscribe(
            ShellProcessIO.Topic.STRING_DATA_STREAM, self.on_shell_output
        )
        self._console = Console()
        self._text_lock = RLock()
        self._text = Text("")

    async def on_mount(self, event: events.Mount) -> None:
        self.set_interval(0.25, self.update_text)

    async def update_text(self):
        with self._text_lock:
            await self.update(self._text, home=False)

    def on_shell_output(self, output: str):
        with self._text_lock:
            self._text.append(Text.from_ansi(output + "\n", no_wrap=True, end=""))
