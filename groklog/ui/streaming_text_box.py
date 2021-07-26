from math import copysign
from typing import List

from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen
from asciimatics.strings import ColouredText
from asciimatics.widgets import TextBox
from asciimatics.widgets.utilities import _enforce_width


class StreamingTextBox(TextBox):
    """
    To increase readability of the FilterViewer code, this intermediary class implements
    some of the necessary functionality for FilterViewer to work. In particular this
    class makes it possible to append lines to the TextBox without having
    O(len(self._value)) operations occur each time a new line is added.

    It also adds some key commands to make it faster and more intuitive when
    scrolling up and down.
    """

    def __init__(self, *args, **kwargs):
        if kwargs.get("line_wrap", None) is not None:
            raise ValueError("'line_wrap' is not modifiable in StreamingTextBox!")
        super().__init__(*args, line_wrap=True, **kwargs)

        # Set up initial _value and _reflowed_text_cache values
        self._value = [ColouredText("", self._parser, colour=None)]
        self._reflowed_text_cache = [(self._value[-1], 0, 0)]

    def process_event(self, event):
        """Override the default up/down behavior in such that pressing up and down
        automatically move the cursor to the top of the page, so that it immediately
        scrolls the view. This is opposed to the TextBox behavior where the user would
        have to press Up until the cursor reaches the top of the page before being able
        to scroll the view.
        """

        if isinstance(event, KeyboardEvent):
            start_line, cursor_line = self.display_line()
            lines_from_top = cursor_line - start_line
            lines_from_bottom = self._h - lines_from_top - 1

            if event.key_code == Screen.KEY_PAGE_UP:
                self._change_display_line(-self._h - lines_from_top, cursor_line)
            elif event.key_code == Screen.KEY_PAGE_DOWN:
                self._change_display_line(self._h + lines_from_bottom, cursor_line)
            elif event.key_code == Screen.KEY_UP:
                self._change_display_line(-lines_from_top - 1, cursor_line)
            elif event.key_code == Screen.KEY_DOWN:
                self._change_display_line(lines_from_bottom + 1, cursor_line)
            else:
                return super().process_event(event)
        else:
            return super().process_event(event)

    def _change_display_line(self, display_delta: int, cursor_line: int):
        """Similar to self._change_line, except the delta will change based on the
        number of display lines."""
        self._column = 0

        new_index = cursor_line + display_delta
        new_index = max(0, min(new_index, len(self._reflowed_text_cache) - 1))
        if new_index == cursor_line:
            # There won't be any change, so just exit early
            return

        _, current_line, _ = self._reflowed_text_cache[cursor_line]
        _, new_line, _ = self._reflowed_text_cache[new_index]

        # This delta wasn't enough to actually change the line, so keep recursively
        # increasing the delta until the line changes
        if current_line == new_line:
            return self._change_display_line(
                int(copysign(1, display_delta)) + display_delta,
                cursor_line=cursor_line,
            )

        self._change_line(new_line - current_line)

    def display_line(self):
        """This logic was modified from the process_event of TextBox. It finds the index
        of _reflowed_text_cache that is currently at the top of the screen, and at the
        cursor.
        """
        cursor_line = 0
        for i, (_, line, col) in enumerate(self._reflowed_text_cache):
            if line < self._line or (line == self._line and col <= self._column):
                cursor_line = i

        # Restrict to visible/valid content.
        start_line = max(
            0, max(cursor_line - self._h + 1, min(self._start_line, cursor_line))
        )
        return start_line, cursor_line

    def add_lines(self, new_lines: List[ColouredText]):
        """Add new lines to the text box.

        This method offers advantages over modifying self._value and calling
        self.reset(), because it adds to the _reflowed_text_cache without clearing it.
        This makes it an O(n) operation, where n is the length of the new lines,
        instead of an O(len(self._value) + n) operation.
        """

        if len(new_lines) == 0:
            return

        self._value += new_lines

        # Exact copy of self.reset(), except _reflowed_text_cache isn't set to None
        self.reset()

        # Append to the _reflowed_text_cache
        limit = self._w - self._offset
        for i, line in enumerate(new_lines, start=self._reflowed_text_cache[-1][1] + 1):
            column = 0
            while self.string_len(str(line)) >= limit:
                sub_string = _enforce_width(
                    line, limit, self._frame.canvas.unicode_aware
                )
                self._reflowed_text_cache.append((sub_string, i, column))
                line = line[len(sub_string) :]
                column += len(sub_string)
            self._reflowed_text_cache.append((line, i, column))

    def reset(self):
        """This mirrors the TextBox.reset() except it doesn't clear the
        _reflowed_text_cache
        """
        self._start_line = 0
        self._start_column = 0
        self._line = len(self._value) - 1
        self._column = 0 if self._is_disabled else len(self._value[self._line])

    @property
    def _reflowed_text(self):
        """Because this class sets the _reflowed_text_cache in the add_stream method, we
        override the TextBox for this property."""
        return self._reflowed_text_cache

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
