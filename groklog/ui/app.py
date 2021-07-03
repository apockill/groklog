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
