import sys

from asciimatics.exceptions import ResizeScreenError
from asciimatics.scene import Scene
from asciimatics.screen import Screen

from groklog.process_node import ShellProcessIO
from groklog.ui import scene_names
from groklog.ui.app import GrokLog
from groklog.ui.filter_creator import FilterCreator


def main():
    # In some systems, curses takes a while to pass Escape key input. More info here:
    # https://github.com/peterbrittain/asciimatics/issues/232
    os.environ.setdefault("ESCDELAY", "0")

    shell = ShellProcessIO()

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
                        screen, filter_model=filter_model, profile_path=save_path
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
