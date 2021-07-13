import copy
from queue import Queue

from asciimatics.parsers import AnsiTerminalParser
from asciimatics.strings import ColouredText
from asciimatics.widgets import TextBox

from groklog.filter_manager import FilterManager
from groklog.process_node import GenericProcessIO, ProcessNode


class FilterViewer(TextBox):
    def __init__(self, filter: GenericProcessIO, height: int):
        super().__init__(
            height,
            name=f"FilterViewer-{filter.name}-{filter.command})",
            readonly=False,
            as_string=False,
            line_wrap=True,
            parser=AnsiTerminalParser(),
        )
        self.filter_manager = filter_manager
        self._data_queue = Queue()
        self.custom_colour = "filter_viewer"

    def process_event(self, event):
        return super().process_event(event)

    def reset(self):
        return super().reset()

    def subscribe_to_filter(self, filter: GenericProcessIO):
        """Reset whatever is being shown, and subscribe the _data_queue to the new
        filter"""

        # Create a new queue so that any previous subscriptions are garbage collected,
        # and so that no text from other filters gets mixed into this new one.
        self._data_queue = Queue()
        filter.subscribe(ProcessNode.Topic.STRING_DATA_STREAM, self._data_queue.put)

        # Clean any existing text and reset the view position
        self._value = [ColouredText("", self._parser, colour=None)]
        self.reset()

    def update(self, frame_no):
        full_stream = ""
        while self._data_queue.qsize():
            full_stream += self._data_queue.get_nowait()
        if len(full_stream):
            self._add_stream(full_stream)

        return super().update(frame_no)

    def _add_stream(self, append_logs: str):
        """Append text to the log stream. This function should receive input from
        the filter and display it."""

        last_colour = self._value[-1].last_colour if len(self._value) else None

        new_value = []
        for line in append_logs.split("\n"):
            value = ColouredText(line, self._parser, colour=last_colour)
            new_value.append(value)
            last_colour = value.last_colour

        # Concatenate existing lines with the new lines
        self._value += new_value

        self.reset()

    @property
    def value(self):
        self._value = [ColouredText("", self._parser, colour=None)]
        return self._value

    @value.setter
    def value(self, value):
        """This value should never be used. It's been replaced by _add_stream"""
        pass
