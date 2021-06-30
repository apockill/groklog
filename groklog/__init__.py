import sys

from asciimatics.exceptions import ResizeScreenError
from asciimatics.scene import Scene
from asciimatics.screen import Screen

from groklog.app import GrokLog


def main():
    def groklog(screen: Screen, old_scene):
        screen.play(
            [Scene([GrokLog(screen)], duration=-1)],
            stop_on_resize=True,
            start_scene=old_scene,
        )

    last_scene = None
    while True:
        try:
            Screen.wrapper(func=groklog, catch_interrupt=False, arguments=[last_scene])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene
        except ValueError as e:
            # Screen will be blank when it's too small. It's better than the
            # application crashing, I suppose
            pass
        except KeyboardInterrupt:
            print("Thank you for using groklog!")
            break


if __name__ == "__main__":
    main()