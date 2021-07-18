from asciimatics.widgets import TextBox
from asciimatics.widgets.utilities import _enforce_width


class StreamingTextBox(TextBox):
    def __init__(self, *args, **kwargs):
        if kwargs.get("line_wrap", None) is not None:
            raise ValueError("'line_wrap' is not modifiable in StreamingTextBox!")
        super().__init__(*args, line_wrap=True, **kwargs)

    def add_lines(self, new_lines):
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
