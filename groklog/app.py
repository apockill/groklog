from asciimatics.widgets import Frame


class GrokLog(Frame):
    def __init__(self, screen):
        super().__init__(
            screen, screen.height, screen.width, has_border=True, name="My Form"
        )
