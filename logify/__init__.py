"""Main TUI implementation for logging-tools

Author: Alex Thiel  
Created: 
"""


import py_cui

__version__ = "v0.0.1"


class App:
    def __init__(self, master):

        self.master = master
        self.master.add_label("Hello py_cui!!!", 1, 1)


def main():
    root = py_cui.PyCUI(3, 3)
    wrapper = App(root)
    root.start()
