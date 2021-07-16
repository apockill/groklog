#!/usr/bin/env python3
import curses
import fcntl
import struct
import termios
from queue import Queue

from asciimatics.event import KeyboardEvent
from asciimatics.parsers import AnsiTerminalParser, Parser
from asciimatics.screen import Canvas, Screen
from asciimatics.widgets import Widget

from groklog.process_node import ShellProcessIO


class Terminal(Widget):
    """
    Widget to handle ansi terminals running a bash shell.
    """

    def __init__(
        self,
        name: str,
        shell: ShellProcessIO,
        height: int,
        show_cursor: bool = True,
    ):
        super().__init__(name)
        self._required_height = height
        self._parser = AnsiTerminalParser()
        self._canvas = None
        self._current_colours = None
        self._cursor_x, self._cursor_y = 0, 0
        self._show_cursor = show_cursor

        # Supported key mappings
        self._map = {}
        for k, v in [
            (Screen.KEY_LEFT, "kcub1"),
            (Screen.KEY_RIGHT, "kcuf1"),
            (Screen.KEY_UP, "kcuu1"),
            (Screen.KEY_DOWN, "kcud1"),
            (Screen.KEY_PAGE_UP, "kpp"),
            (Screen.KEY_PAGE_DOWN, "knp"),
            (Screen.KEY_HOME, "khome"),
            (Screen.KEY_END, "kend"),
            (Screen.KEY_DELETE, "kdch1"),
            (Screen.KEY_BACK, "kbs"),
        ]:
            self._map[k] = curses.tigetstr(v)
        self._map[Screen.KEY_TAB] = "\t".encode()

        # Subscribe to shell data
        self._data_queue = Queue()
        self._shell = shell

    def update(self, frame_no):
        """Draw the current terminal content to screen."""
        # Push current terminal output to screen.
        self._canvas.refresh()

        # Drain the shell queue of any data that built up between frames
        full_stream = ""
        while self._data_queue.qsize():
            full_stream += self._data_queue.get_nowait()
        if len(full_stream):
            self._add_stream(full_stream)

        # Draw cursor if needed.
        if frame_no % 20 < 10 and self._show_cursor:
            origin = self._canvas.origin
            x = self._cursor_x + origin[0]
            y = self._cursor_y + origin[1] - self._canvas.start_line
            details = self._canvas.get_from(self._cursor_x, self._cursor_y)
            if details:
                char, colour, attr, bg = details
                attr |= Screen.A_REVERSE
                self._frame.canvas.print_at(chr(char), x, y, colour, attr, bg)

    def set_layout(self, x, y, offset, w, h):
        """
        Resize the widget (and underlying TTY) to the required size.
        """
        super().set_layout(x, y, offset, w, h)
        self._canvas = Canvas(self._frame.canvas, h, w, x=x, y=y)
        winsize = struct.pack("HHHH", h, w, 0, 0)
        fcntl.ioctl(self._shell._slave, termios.TIOCSWINSZ, winsize)

    def process_event(self, event):
        """
        Pass any recognised input on to the TTY.
        """
        if isinstance(event, KeyboardEvent):
            if event.key_code > 0:
                val = chr(event.key_code).encode()
            elif event.key_code in self._map:
                val = self._map[event.key_code]
            self._shell.write(val)
            return
        return event

    def _add_stream(self, value: str):
        """
        Process any output from the TTY.
        """
        canvas_height, _ = self._canvas.dimensions

        # Limit the value to either the last 10k characters, or the last canvas_height
        # lines. This performance optimization makes it impossible to have the UI block
        # for too long just to render a massive set of logs.
        lines = value[-10000:].split("\n")[-canvas_height:]

        for i, line in enumerate(lines):
            self._parser.reset(line, self._current_colours)
            for offset, command, params in self._parser.parse():
                if command == Parser.DISPLAY_TEXT:
                    # Just display the text...  allowing for line wrapping.
                    if self._cursor_x + len(params) > self._w:
                        part_1 = params[: self._w - self._cursor_x]
                        part_2 = params[self._w - self._cursor_x :]
                        self._print_at(part_1, self._cursor_x, self._cursor_y)
                        self._print_at(part_2, 0, self._cursor_y + 1)
                        self._cursor_x = len(part_2)
                        self._cursor_y += 1
                        if self._cursor_y - self._canvas.start_line >= self._h:
                            self._canvas.scroll()
                    else:
                        self._print_at(params, self._cursor_x, self._cursor_y)
                        self._cursor_x += len(params)
                elif command == Parser.CHANGE_COLOURS:
                    # Change current text colours.
                    self._current_colours = params
                elif command == Parser.NEXT_TAB:
                    # Move to next tab stop - hard-coded to default of 8 characters.
                    self._cursor_x = (self._cursor_x // 8) * 8 + 8
                elif command == Parser.MOVE_RELATIVE:
                    # Move cursor relative to current position.
                    self._cursor_x += params[0]
                    self._cursor_y += params[1]
                    if self._cursor_y < self._canvas.start_line:
                        self._canvas.scroll(self._cursor_y - self._canvas.start_line)
                elif command == Parser.MOVE_ABSOLUTE:
                    # Move cursor relative to specified absolute position.
                    if params[0] is not None:
                        self._cursor_x = params[0]
                    if params[1] is not None:
                        self._cursor_y = params[1] + self._canvas.start_line
                elif command == Parser.DELETE_LINE:
                    # Delete some/all of the current line.
                    if params == 0:
                        self._print_at(
                            " " * (self._w - self._cursor_x),
                            self._cursor_x,
                            self._cursor_y,
                        )
                    elif params == 1:
                        self._print_at(" " * self._cursor_x, 0, self._cursor_y)
                    elif params == 2:
                        self._print_at(" " * self._w, 0, self._cursor_y)
                elif command == Parser.DELETE_CHARS:
                    # Delete n characters under the cursor.
                    for x in range(self._cursor_x, self._w):
                        if x + params < self._w:
                            cell = self._canvas.get_from(x + params, self._cursor_y)
                        else:
                            cell = (
                                ord(" "),
                                self._current_colours[0],
                                self._current_colours[1],
                                self._current_colours[2],
                            )
                        self._canvas.print_at(
                            chr(cell[0]),
                            x,
                            self._cursor_y,
                            colour=cell[1],
                            attr=cell[2],
                            bg=cell[3],
                        )
                elif command == Parser.SHOW_CURSOR:
                    # Show/hide the cursor.
                    self._show_cursor = params
                elif command == Parser.CLEAR_SCREEN:
                    # Clear the screen.
                    self._canvas.clear_buffer(
                        self._current_colours[0],
                        self._current_colours[1],
                        self._current_colours[2],
                    )
            # Move to next line, scrolling buffer as needed.
            if i != len(lines) - 1:
                self._cursor_x = 0
                self._cursor_y += 1
                if self._cursor_y - self._canvas.start_line >= self._h:
                    self._canvas.scroll()

    def _print_at(self, text, x, y):
        """
        Helper function to simplify use of the canvas.
        """
        self._canvas.print_at(
            text,
            x,
            y,
            colour=self._current_colours[0],
            attr=self._current_colours[1],
            bg=self._current_colours[2],
        )

    def reset(self):
        """
        Reset the widget to a blank screen.
        """
        self._canvas = Canvas(
            self._frame.canvas, self._h, self._w, x=self._x, y=self._y
        )
        self._cursor_x, self._cursor_y = 0, 0
        self._current_colours = (
            Screen.COLOUR_WHITE,
            Screen.A_NORMAL,
            Screen.COLOUR_BLACK,
        )

        # Unsubscribe and resubscribe to the stream to get back the full history
        if self._shell.is_subscribed(
            ShellProcessIO.Topic.STRING_DATA_STREAM, self._data_queue.put
        ):
            self._shell.unsubscribe(
                ShellProcessIO.Topic.STRING_DATA_STREAM, self._data_queue.put
            )

        # TODO: unsubscribing and subscribing with block=False is NOT thread safe.
        #       for that reason, we set blocking=True for this call. Investigate
        #       making a robust shell.is_subscribed call.
        self._shell.subscribe_with_history(
            ShellProcessIO.Topic.STRING_DATA_STREAM, self._data_queue.put, blocking=True
        )

    def required_height(self, offset, width):
        """
        Required height for the terminal.
        """
        return self._required_height

    @property
    def frame_update_count(self):
        """
        Frame update rate required.
        """
        # Force refresh for cursor.
        return 1 if self._has_focus else 0

    @property
    def value(self):
        """
        Terminal value - not needed for demo.
        """
        return

    @value.setter
    def value(self, _):
        return
