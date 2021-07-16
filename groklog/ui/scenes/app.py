from functools import partial

from asciimatics import widgets
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen
from asciimatics.widgets import Layout

from groklog.filter_manager import FilterManager
from groklog.process_node import ShellProcessIO
from groklog.ui.filter_viewer import FilterViewer
from groklog.ui.terminal import Terminal

from . import scene_names
from .base_app import BaseApp


class GrokLog(BaseApp):
    def __init__(self, screen, filter_manager: FilterManager):
        super().__init__(
            screen,
            screen.height,
            screen.width,
            can_scroll=False,
            name="GrokLog",
            title="GrokLog",
        )
        self.filter_manager = filter_manager

        # Register all of the filter widgets
        self._filter_widgets = {}
        for filter in self.filter_manager:
            self._register_filter(filter)

        self.central_layout = Layout([100], fill_frame=True)
        self.add_layout(self.central_layout)
        self.view_filter(self.filter_manager.selected_filter)

        # Create the Tab Layout and buttons for it
        self.tab_layout = Layout([1, 0, 1, 1, 1, 1, 1])
        self.add_layout(self.tab_layout)
        self.create_tab_buttons()

        self.fix()

    def reset(self):
        # After coming back from the AddFilter call, recreate the tab buttons to fill
        # in any missing tabs.
        for filter in self.filter_manager:
            if filter not in self._filter_widgets:
                self._register_filter(filter)

        self.create_tab_buttons()
        return super().reset()

    def _register_filter(self, filter):
        """Create a widget for this filter and save it under self._filter_widgets"""
        if filter in self._filter_widgets:
            # This filter is already registered.
            return

        if isinstance(filter, ShellProcessIO):
            widget = Terminal(
                name="term",
                shell=filter,
                height=widgets.Widget.FILL_COLUMN,
            )
        else:
            widget = FilterViewer(filter=filter, height=widgets.Widget.FILL_COLUMN)

        self._filter_widgets[filter] = widget

    def view_filter(self, filter):
        """Change the actively shown central widget"""
        if self.scene is not None:
            self.display_toast(f"Viewing {filter.name}: '{filter.command}'")

        self.filter_manager.selected_filter = filter

        # Replace the central layout widget
        new_widget = self._filter_widgets[filter]
        self.central_layout.clear_widgets()
        self.central_layout.add_widget(new_widget)
        self.central_layout.add_widget(widgets.Divider())

        if isinstance(new_widget, Terminal):
            # The terminal has a... hard time keeping stuff on the screen. This forces
            # the terminal to re-subscribe and refresh the screen.
            # TODO: Investigate why the terminal doesn't redraw it's screen correctly
            new_widget.reset()

        # This seems to put the widget into the update() loop
        self.fix()
        self.central_layout.focus(force_widget=new_widget)
        self.screen.force_update(full_refresh=True)

    def create_tab_buttons(self):
        """Create all of the tab buttons again"""
        self.tab_layout.clear_widgets()
        self.tab_layout.add_widget(
            widgets.Button(
                text="Add Filter",
                on_click=partial(self.change_scene, scene_names.FILTER_CREATOR_SCENE),
            ),
            column=0,
        )
        self.tab_layout.add_widget(widgets.VerticalDivider(), column=1)

        for column, filter in enumerate(self.filter_manager, 2):
            self.tab_layout.add_widget(
                widgets.Button(
                    text=filter.name,
                    on_click=lambda filter=filter: self.view_filter(filter),
                ),
                column=column,
            )

        self.fix()

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.key_code in [Screen.ctrl("c")]:
                # Catch Ctrl+C and pass it on to the sub shell
                self.display_toast("Press Escape to close GrokLog!")
                if (
                    self.filter_manager.selected_filter
                    is self.filter_manager.root_filter
                ):
                    self.filter_manager.root_filter.send_sigint()
                return

        return super().process_event(event)
