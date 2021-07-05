from functools import partial

from asciimatics import widgets
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen
from asciimatics.widgets import Layout

from groklog.process_node import ShellProcessIO
from groklog.ui.base_app import BaseApp
from groklog.ui.terminal import Terminal


class GrokLog(BaseApp):
    def __init__(self, screen, shell: ShellProcessIO):
        super().__init__(
            screen,
            screen.height,
            screen.width,
            has_border=True,
            name="GrokLog",
            title="GrokLog",
        )

        self.shell = shell

        # Create the Shell layout
        shell_layout = Layout([100], fill_frame=True)
        terminal = Terminal(name="term", shell=shell, height=widgets.Widget.FILL_COLUMN)
        self.add_layout(shell_layout)
        shell_layout.add_widget(terminal)
        shell_layout.add_widget(widgets.Divider())

        # Create the Tab Layout and buttons for it
        add_filter_button = widgets.Button(
            "Add Filter", lambda: self.display_toast("benis")
        )

        tab_layout = Layout([1, 0, 1, 1, 1, 1, 1])
        self.add_layout(tab_layout)
        tab_layout.add_widget(add_filter_button, 0)
        tab_layout.add_widget(widgets.VerticalDivider(), 1)

        self.fix()
        self.set_theme("monochrome")

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.key_code in [Screen.ctrl("c")]:
                # Catch Ctrl+C and pass it on to the sub shell
                self.display_toast("Press Escape to close GrokLog!")
                self.shell.send_sigint()
                return

        super().process_event(event)
