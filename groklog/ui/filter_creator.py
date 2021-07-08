from asciimatics import effects, renderers, widgets
from asciimatics.exceptions import InvalidFields
from asciimatics.widgets import Frame, Layout

from groklog.filter_model import DuplicateFilterError, FilterModel
from groklog.ui import scene_names
from groklog.ui.base_app import BaseApp


class FilterCreator(BaseApp):
    _NEW_FILTER_PARAMETERS_COLUMN = 0
    _SYSTEM_SETTINGS_COLUMN = 1
    _SAVE_PATH_LABEL = "save_path"

    def __init__(self, screen, filter_model: FilterModel, profile_path: Path):
        super().__init__(
            screen,
            screen.height,
            screen.width,
            has_border=True,
            can_scroll=True,
            name="Benis",
            title="Create Filter",
        )
        self._filter_model = filter_model

        dialog_layout = Layout([1, 1], fill_frame=True)

        self.add_layout(dialog_layout)

        # Add the widgets for the left column
        self.profile_path = profile_path
        save_path_widget = widgets.Text(
            label="Save Profile At",
            name=self._SAVE_PATH_LABEL,
            on_change=None,
            validator=None,
        )
        dialog_layout.add_widget(save_path_widget, column=self._SYSTEM_SETTINGS_COLUMN)

        # Add the widgets for the right column
        dialog_layout.add_widget(
            widgets.DropdownList(
                options=[(f.name, i + 1) for i, f in enumerate(self._filter_model)],
                label="Input Process",
                name=FilterModel.FILTER_PARENT,
            ),
            column=self._NEW_FILTER_PARAMETERS_COLUMN,
        )
        dialog_layout.add_widget(
            widgets.Text(
                label="Filter Name",
                name=FilterModel.FILTER_NAME,
                validator=lambda val: 0 < len(val) < 10,
            ),
            column=self._NEW_FILTER_PARAMETERS_COLUMN,
        )
        dialog_layout.add_widget(
            widgets.Text(
                label="Command",
                name=FilterModel.FILTER_COMMAND,
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
        save_cancel_layout = Layout([10, 1, 1, 1])
        self.add_layout(save_cancel_layout)
        save_cancel_layout.add_widget(widgets.VerticalDivider(), 1)
        save_cancel_layout.add_widget(save_filter_button, 2)
        save_cancel_layout.add_widget(cancel_filter_button, 3)

        self.fix()

    def save_filters(self):
        # TOOD: Add logic to save things here
        try:
            self.save(validate=True)
        except InvalidFields:
            self.display_popup("Please fill in all of the fields!", ["Ok"])
            return

        try:
            self._filter_model.create_filter(
                name=self.data[FilterModel.FILTER_NAME],
                command=self.data[FilterModel.FILTER_COMMAND],
                parent=self.data[FilterModel.FILTER_PARENT],
            )
        except DuplicateFilterError:
            self.display_popup("There already exists a filter with that name!", ["Ok"])
            return

        self.reset()
        self.change_scene(scene_name=scene_names.SHELL_VIEW)

    def reset(self):
        super().reset()
        self.data = {
            FilterModel.FILTER_PARENT: 1,
            FilterModel.FILTER_NAME: "",
            FilterModel.FILTER_COMMAND: "",
            self._SAVE_PATH_LABEL: str(self.profile_path),
        }

    def cancel_contents(self):
        self.reset()
        self.change_scene(scene_name=scene_names.SHELL_VIEW)
