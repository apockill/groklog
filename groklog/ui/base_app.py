from asciimatics import effects, renderers
from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import NextScene, StopApplication
from asciimatics.screen import Screen

from .theming import set_theme

class BaseApp(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        set_theme(self)

    def change_scene(self, scene_name: str):
        raise NextScene(scene_name)

    def display_toast(self, message):
        """Display a temporary message for a few seconds near the bottom of
        the screen."""
        self._scene.add_effect(
            effects.Print(
                self.screen,
                renderers.SpeechBubble(text=message, uni=True),
                speed=1,
                transparent=False,
                clear=True,
                delete_count=30,
                y=int(self.screen.height * 0.8),
            ),
        )

    def process_event(self, event):
        """Handle shutting down the program if escape is pressed"""
        if isinstance(event, KeyboardEvent):
            if event.key_code in (Screen.KEY_ESCAPE, Screen.KEY_END):
                # Close the program when Escape or End is pressed
                raise StopApplication("")
        super().process_event(event)
