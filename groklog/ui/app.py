from textual.app import App
from textual.widgets import Header

from groklog.filter_manager import FilterManager
from groklog.process_node import ShellProcessIO
from groklog.ui.command_text_box import CommandTextbox
from .filter_viewer import FilterViewer


class GroklogApp(App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.filter_manager = FilterManager(shell=ShellProcessIO())

    async def on_mount(self) -> None:
        output = FilterViewer(process_node=self.filter_manager.root_filter)
        in_put = CommandTextbox(to_process_node=self.filter_manager.root_filter)

        grid = await self.view.dock_grid(edge="left", name="left")
        grid.add_column(fraction=1, name="u")
        grid.add_row(fraction=1, name="top", min_size=3)
        grid.add_row(fraction=20, name="middle")
        grid.add_row(fraction=1, name="bottom", min_size=3)
        grid.add_areas(area1="u,top", area2="u,middle", area3="u,bottom")
        grid.place(
            area1=Header(),
            area2=output,
            area3=in_put,
        )

        await self.set_focus(in_put)
