import copy
from queue import Queue
from typing import Generator, List, Tuple

from asciimatics.parsers import AnsiTerminalParser
from asciimatics.strings import ColouredText
from asciimatics.widgets import TextBox

from groklog.process_node import GenericProcessIO, ProcessNode

_line_cache = {}


def _cached_coloured_text(
    lines: List[str],
    last_colour: Tuple,
    from_filter: ProcessNode,
    parser: AnsiTerminalParser,
) -> Generator[ColouredText, None, None]:
    """This generator yields coloured text for each of the lines. It caches results
    along the way, so that any duplicate lines in the future are yieled immediately with
    no duplicate processing. """

    filter_key = from_filter.name + from_filter.command

    for line in lines:
        cache_key = (line, last_colour, filter_key)

        # Yield cached results if they exist
        if cache_key in _line_cache:
            yield _line_cache[cache_key]
            continue

        try:
            value = ColouredText(line, parser, colour=last_colour)
        except IndexError:
            continue
        _line_cache[cache_key] = value
        yield value
        last_colour = tuple(value.last_colour)


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

        filter.subscribe_with_history(
            ProcessNode.Topic.STRING_DATA_STREAM, self._add_stream, blocking=False
        )

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

        processed_lines = []
        for colored_line in _cached_coloured_text(
            lines=append_logs.split("\n"),
            last_colour=tuple(self._value[-1].last_colour),
            from_filter=self.filter,
            parser=self._parser,
        ):
            processed_lines.append(colored_line)

            # If the UI has nothing to show, then send what's been processed so far.
            # Otherwise the UI hasn't gotten around to showing what's already in the
            # queue, so just hold onto the processed lines for now.
            if self._processed_data_queue.qsize() == 0:
                self._processed_data_queue.put(processed_lines)
                processed_lines = []

        # Release any processed lines that haven't been released yet.
        self._processed_data_queue.put(processed_lines)

    @property
    def value(self):
        self._value = [ColouredText("", self._parser, colour=None)]
        return self._value

    @value.setter
    def value(self, value):
        """This value should never be used. It's been replaced by _add_stream"""
        pass

    @property
    def frame_update_count(self):
        return 1 if self._has_focus else 0
