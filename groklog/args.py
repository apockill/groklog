from argparse import ArgumentParser
from pathlib import Path

import appdirs

long_description = """
Welcome to GrokLog!

GrokLog is a tool for creating process trees, where a root process (an ordinary shell)
has it's output piped into the stdin of other processes. This allows you to easily 
build complex pipe filters, while viewing the output every step of the way. 

On top of that, building profiles is quick and easy, so after configuring for one use 
case, you can easily load that profile up again!
"""


def parse_args():
    parser = ArgumentParser(description=long_description)

    default_save_path = Path(
        appdirs.user_config_dir(appname="groklog", appauthor="Alex Thiel")
    )

    parser.add_argument(
        "--profile-directory",
        default=default_save_path,
        help="Override the default directory to load profiles from.",
    )

    parser.add_argument(
        "profile",
        type=str,
        nargs="?",
        default="default",
        help="Load a custom profile. If nothing is entered, the default profile "
        f"at {default_save_path / 'default.json'} will be used.",
    )

    return parser.parse_args()
