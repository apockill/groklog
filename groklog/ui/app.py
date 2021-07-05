from asciimatics import widgets
from asciimatics.widgets import Frame, Layout

from groklog.shell import Shell
from groklog.ui.terminal import Terminal


class GrokLog(Frame):
    def __init__(self, screen, shell: Shell):
        super().__init__(
            screen, screen.height, screen.width, has_border=True, name="GrokLog"
        )
        self.shell = shell

        # Create the widgets for the demo.
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Terminal(name="term", shell=shell, height=25))
        layout.add_widget(Terminal(name="term", shell=shell, height=25))
        layout.add_widget(Terminal(name="term", shell=shell, height=25))
        # layout.add_widget(Terminal(name="term", shell=shell, height=Widget.FILL_FRAME))
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
