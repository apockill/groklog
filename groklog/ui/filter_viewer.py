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
        self._text_changed: bool = False

    async def on_mount(self, event: events.Mount) -> None:
        self.set_interval(0.25, self.update_text)

    async def update_text(self):
        if not self._text_changed:
            return

        with self._text_lock:
            await self.update(self._text, home=False)

        # Scroll to the bottom
        await self.key_end()

        # Reset the text changed flag
        self._text_changed = False

    @property
    def bottom_y(self):
        return self.window.virtual_size.height - self.size.height

    def on_shell_output(self, output: str):
        with self._text_lock:
            if len(output.strip()) == 0:
                return

            self._text_changed = True
            self._text.append(Text.from_ansi(output + "\n", no_wrap=True, end=""))
