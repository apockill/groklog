from pathlib import Path

from asciimatics import effects, renderers, widgets
from asciimatics.exceptions import InvalidFields
from asciimatics.widgets import Frame, Layout

from groklog.filter_manager import DuplicateFilterError, FilterManager

from . import scene_names
from .base_app import BaseApp


class FilterCreator(BaseApp):
    _NEW_FILTER_PARAMETERS_COLUMN = 1
    _SYSTEM_SETTINGS_COLUMN = 3
    _SAVE_PATH_LABEL = "save_path"

    def __init__(self, screen, filter_manager: FilterManager, profile_path: Path):
        super().__init__(
            screen,
            screen.height,
            screen.width,
            has_border=True,
            can_scroll=True,
            name="Benis",
            title="Create Filter",
        )
        self._filter_manager: FilterManager = filter_manager
        self.profile_path: Path = profile_path

        dialog_layout = Layout([1, 30, 1, 30, 1], fill_frame=True)

        self.add_layout(dialog_layout)

        # Add the widgets for the left column
        dialog_layout.add_widget(
            widgets.Label("System Configuration", align="^", height=2),
            column=self._SYSTEM_SETTINGS_COLUMN,
        )
        dialog_layout.add_widget(
            widgets.Text(
                label="Save Path",
                name=self._SAVE_PATH_LABEL,
                on_change=None,
                validator=None,
            ),
            column=self._SYSTEM_SETTINGS_COLUMN,
        )

        # Add the widgets for the right column
        dialog_layout.add_widget(
            widgets.Label("New Filter Parameters", align="^", height=2),
            column=self._NEW_FILTER_PARAMETERS_COLUMN,
        )
        self.source_drop_down = widgets.DropdownList(
            options=[],
            label="Input Source",
            name=FilterManager.FILTER_PARENT,
        )

        dialog_layout.add_widget(
            self.source_drop_down, column=self._NEW_FILTER_PARAMETERS_COLUMN
        )
        dialog_layout.add_widget(
            widgets.Text(
                label="Filter Name",
                name=FilterManager.FILTER_NAME,
                validator=lambda val: 0 < len(val) < 15,
            ),
            column=self._NEW_FILTER_PARAMETERS_COLUMN,
        )
        dialog_layout.add_widget(
            widgets.Text(
                label="Command",
                name=FilterManager.FILTER_COMMAND,
                validator=lambda val: len(val) > 0,
            ),
            column=self._NEW_FILTER_PARAMETERS_COLUMN,
        )

        # I put two dividers here, one invisible. The invisible one pushes the
        # visible one all the way to the bottom, otherwise, it'll appear in the
        # middle.
        for column in range(len(dialog_layout._columns)):
            dialog_layout.add_widget(
                widgets.Divider(height=widgets.Widget.FILL_FRAME, draw_line=False),
                column=column,
            )
            dialog_layout.add_widget(widgets.Divider(), column=column)

        # Create the Tab Layout and buttons for it
        save_filter_button = widgets.Button("Save", self.save_filters)
        cancel_filter_button = widgets.Button("Cancel", self.cancel_contents)
        save_cancel_layout = Layout([7, 1, 1])
        self.add_layout(save_cancel_layout)
        save_cancel_layout.add_widget(save_filter_button, 1)
        save_cancel_layout.add_widget(cancel_filter_button, 2)

        self.fix()

    def save_filters(self):
        # TOOD: Add logic to save things here
        try:
            self.save(validate=True)
        except InvalidFields:
            self.display_popup("Please fix any fields highlighted in yellow.", ["Ok"])
            return

        try:
            parent_index = self.data[FilterManager.FILTER_PARENT]
            parent_name = self.source_drop_down.options[parent_index][0]
            parent_filter = self._filter_manager.get_filter(parent_name)
            self._filter_manager.create_filter(
                name=self.data[FilterManager.FILTER_NAME],
                command=self.data[FilterManager.FILTER_COMMAND],
                parent=parent_filter,
            )
        except DuplicateFilterError:
            self.display_popup("There already exists a filter with that name!", ["Ok"])
            return
        self.profile_path = Path(self.data[self._SAVE_PATH_LABEL])

        self._filter_manager.save_profile(self.profile_path)

        self.reset()
        self.change_scene(scene_name=scene_names.SHELL_VIEW)

    def reset(self):
        self.source_drop_down.options = [
            (f.name, i) for i, f in enumerate(self._filter_manager)
        ]
        super().reset()
        self.data = {
            FilterManager.FILTER_PARENT: 0,
            FilterManager.FILTER_NAME: "",
            FilterManager.FILTER_COMMAND: "",
            self._SAVE_PATH_LABEL: str(self.profile_path),
        }

    def cancel_contents(self):
        self.reset()
        self.change_scene(scene_name=scene_names.SHELL_VIEW)
