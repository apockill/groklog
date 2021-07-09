import os
import sys

from asciimatics.exceptions import ResizeScreenError
from asciimatics.scene import Scene
from asciimatics.screen import Screen

from groklog.args import parse_args
from groklog.filter_manager import FilterManager
from groklog.process_node import ShellProcessIO
from groklog.ui import scene_names
from groklog.ui.app import GrokLog
from groklog.ui.filter_creator import FilterCreator

from .version import __version__


def main():
    # In some systems, curses takes a while to pass Escape key input. More info here:
    # https://github.com/peterbrittain/asciimatics/issues/232
    os.environ.setdefault("ESCDELAY", "0")
    args = parse_args()

    shell = ShellProcessIO()
    filter_manager = FilterManager(shell=shell)

    # Load configuration
    save_path = args.profile_directory / (args.profile + ".json")
    if save_path.is_file():
        filter_manager.load_profile(save_path)

    def groklog(screen: Screen, scene):
        scenes = [
            Scene(
                [GrokLog(screen, shell=shell)],
                duration=-1,
                name=scene_names.SHELL_VIEW,
            ),
            Scene(
                [
                    FilterCreator(
                        screen, filter_manager=filter_manager, profile_path=save_path
                    )
                ],
                duration=-1,
                name=scene_names.FILTER_CREATOR_SCENE,
            ),
        ]

        screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)

    last_scene = None
    while True:
        try:
            Screen.wrapper(func=groklog, catch_interrupt=True, arguments=[last_scene])
            print("Thank you for using GrokLog!")
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene
        except ValueError as e:
            # Screen will be blank when it's too small. It's better than the
            # application crashing, I suppose
            pass


if __name__ == "__main__":
    main()
