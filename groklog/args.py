from argparse import ArgumentParser
from pathlib import Path

import appdirs

long_description = """
Welcome to GrokLog!

GrokLog is a tool for creating "process trees", that is, a root process (an ordinary shell)
has its output piped into the stdin of other processes. Those other processes can in 
turn have _their_ stdout piped into even more processes. Then, groklog lets you view the 
stdout of every process in the tree. 
 
The benefit of all of this is that you can filter logs or other streams using the 
various unix tools you are already familiar with, and do so in a much more sophisticated 
way. 

On top of that, building profiles is quick and easy, so after spending some time 
configuring, everything is saved to a profile and the next time you run groklog you can 
jump right in where you left off!
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
