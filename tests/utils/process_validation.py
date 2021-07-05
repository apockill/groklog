import subprocess

import psutil


def verify_all_child_processes_closed():
    current_proc = psutil.Process()
    children = current_proc.children()
    if len(children) != 0:
        raise EnvironmentError(
            "Not all child processes were shut down! Currently running processes:"
            + str(children)
        )
