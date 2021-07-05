import sys

from asciimatics.exceptions import ResizeScreenError
from asciimatics.scene import Scene
from asciimatics.screen import Screen

from groklog.process_node import ShellProcessIO
from groklog.ui.app import GrokLog


def main():
    shell = ShellProcessIO()

    def groklog(screen: Screen, old_scene):
        screen.play(
            [Scene([GrokLog(screen, shell=shell)], duration=-1)],
            stop_on_resize=True,
            start_scene=old_scene,
            allow_int=True,
        )

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
