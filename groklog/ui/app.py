from asciimatics import effects, renderers, widgets
from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import StopApplication
from asciimatics.screen import Screen
from asciimatics.widgets import Frame, Layout

from groklog.process_node import ShellProcessIO
from groklog.ui.terminal import Terminal


class GrokLog(Frame):
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
        tab_layout = Layout([1, 1, 1, 1, 1, 1, 1])
        self.add_layout(tab_layout)
        tab_layout.add_widget(add_filter_button, 0)
        tab_layout.add_widget(widgets.VerticalDivider(), 1)

        self.fix()
        self.set_theme("monochrome")

    def display_toast(self, message):
        """Display a temporary message for a few seconds near the bottom of
        the screen."""
        self._scene.add_effect(
            effects.Print(
                self.screen,
                renderers.StaticRenderer(images=[message]),
                bg=Screen.COLOUR_YELLOW,
                colour=Screen.COLOUR_BLACK,
                speed=0,
                transparent=False,
                clear=True,
                delete_count=30,
                y=self.screen.height - 3,
            )
        )

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.key_code in [Screen.ctrl("c")]:
                # Catch Ctrl+C and pass it on to the sub shell
                self.display_toast("Press Escape to close GrokLog!")
                self.shell.send_sigint()
                return
            elif event.key_code in (Screen.KEY_ESCAPE, Screen.KEY_END):
                # Close the program when Escape or End is pressed
                raise StopApplication("")
        super().process_event(event)
