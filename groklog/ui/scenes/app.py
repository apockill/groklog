from functools import partial

from asciimatics import widgets
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen
from asciimatics.widgets import Layout

from groklog.filter_manager import FilterManager
from groklog.ui.terminal import Terminal

from . import scene_names
from .base_app import BaseApp


class GrokLog(BaseApp):
    def __init__(self, screen, filter_manager: FilterManager):
        super().__init__(
            screen,
            screen.height,
            screen.width,
            has_border=True,
            can_scroll=False,
            name="GrokLog",
            title="GrokLog",
        )
        self.filter_manager = filter_manager

        # Create the Shell layout
        shell_layout = Layout([100], fill_frame=True)
        terminal = Terminal(
            name="term",
            shell=filter_manager.root_filter,
            height=widgets.Widget.FILL_COLUMN,
        )
        self.add_layout(shell_layout)
        shell_layout.add_widget(terminal)
        shell_layout.add_widget(widgets.Divider())

        # Create the Tab Layout and buttons for it
        add_filter_button = widgets.Button(
            "Add Filter", partial(self.change_scene, scene_names.FILTER_CREATOR_SCENE)
        )

        tab_layout = Layout([1, 0, 1, 1, 1, 1, 1])
        self.add_layout(tab_layout)
        tab_layout.add_widget(add_filter_button, 0)
        tab_layout.add_widget(widgets.VerticalDivider(), 1)

        self.fix()

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.key_code in [Screen.ctrl("c")]:
                # Catch Ctrl+C and pass it on to the sub shell
                self.display_toast("Press Escape to close GrokLog!")
                self.filter_manager.root_filter.send_sigint()
                return

        return super().process_event(event)
