from asciimatics import widgets
from asciimatics.screen import Screen

GROKLOG_THEME = {
    "background": (Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK),
    "shadow": (Screen.COLOUR_WHITE, None, Screen.COLOUR_WHITE),
    "disabled": (Screen.COLOUR_WHITE, Screen.A_BOLD, Screen.COLOUR_BLACK),
    "invalid": (Screen.COLOUR_WHITE, Screen.A_BOLD, Screen.COLOUR_YELLOW),
    "label": (Screen.COLOUR_BLUE, Screen.A_BOLD, Screen.COLOUR_BLACK),
    "borders": (Screen.COLOUR_WHITE, Screen.A_BOLD, Screen.COLOUR_BLACK),
    "scroll": (Screen.COLOUR_CYAN, Screen.A_NORMAL, Screen.COLOUR_BLACK),
    "title": (Screen.COLOUR_WHITE, Screen.A_BOLD, Screen.COLOUR_BLACK),
    "edit_text": (Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK),
    "focus_edit_text": (Screen.COLOUR_WHITE, Screen.A_BOLD, Screen.COLOUR_CYAN),
    "readonly": (Screen.COLOUR_WHITE, Screen.A_BOLD, Screen.COLOUR_BLACK),
    "focus_readonly": (Screen.COLOUR_CYAN, Screen.A_BOLD, Screen.COLOUR_CYAN),
    "button": (Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK),
    "focus_button": (Screen.COLOUR_WHITE, Screen.A_BOLD, Screen.COLOUR_CYAN),
    "control": (Screen.COLOUR_YELLOW, Screen.A_NORMAL, Screen.COLOUR_BLACK),
    "selected_control": (Screen.COLOUR_YELLOW, Screen.A_BOLD, Screen.COLOUR_BLACK),
    "focus_control": (Screen.COLOUR_YELLOW, Screen.A_NORMAL, Screen.COLOUR_BLACK),
    "selected_focus_control": (
        Screen.COLOUR_YELLOW,
        Screen.A_BOLD,
        Screen.COLOUR_CYAN,
    ),
    "field": (Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK),
    "selected_field": (Screen.COLOUR_YELLOW, Screen.A_BOLD, Screen.COLOUR_BLACK),
    "focus_field": (Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK),
    "selected_focus_field": (
        Screen.COLOUR_WHITE,
        Screen.A_BOLD,
        Screen.COLOUR_CYAN,
    ),
    # This is a custom color for the FilterViewer widget
    "filter_viewer": (Screen.COLOUR_DEFAULT, Screen.A_BOLD, Screen.COLOUR_BLACK),
}

warning = widgets.utilities.THEMES["warning"]
warning["shadow"] = (Screen.COLOUR_BLACK, None, Screen.COLOUR_WHITE)


def set_theme(frame):
    widgets.utilities.THEMES["groklog"] = GROKLOG_THEME
    frame.set_theme("groklog")
