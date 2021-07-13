import copy
from queue import Queue

from asciimatics.parsers import AnsiTerminalParser
from asciimatics.strings import ColouredText
from asciimatics.widgets import TextBox

from groklog.process_node import GenericProcessIO, ProcessNode


class FilterViewer(TextBox):
    def __init__(self, filter: GenericProcessIO, height: int):
        super().__init__(
            height,
            name=f"FilterViewer-{filter.name}-{filter.command})",
            readonly=True,
            as_string=False,
            line_wrap=True,
            parser=AnsiTerminalParser(),
        )
        self.filter = filter
        self._data_queue = Queue()
        self.custom_colour = "filter_viewer"
        self._value = [ColouredText("", self._parser, colour=None)]

        # Create subscriptions
        self._processed_data_queue = Queue()
        """self._add_stream pushes to here, and self.update pulls the results"""
        filter.subscribe(ProcessNode.Topic.STRING_DATA_STREAM, self._add_stream)

    def process_event(self, event):
        return super().process_event(event)

    def update(self, frame_no):
        while self._processed_data_queue.qsize():
            self._value += self._processed_data_queue.get_nowait()

        self.reset()

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

        # Put this in a queue to be picked up by the main thread, in self.update
        self._processed_data_queue.put(new_value)

    @property
    def value(self):
        self._value = [ColouredText("", self._parser, colour=None)]
        return self._value

    @value.setter
    def value(self, value):
        """This value should never be used. It's been replaced by _add_stream"""
        pass
