import fcntl
import os
import pty
import select
import subprocess
from enum import Enum, auto
from threading import RLock, Thread

from .base import ProcessNode


class ShellProcessIO(ProcessNode):
    """
    The widget will start a bash shell in the background and use a pseudo TTY to control it.  It then
    starts a thread to transfer any data between the two processes (the one running this widget and
    the bash shell).
    """

    class Topic(Enum):
        STRING_DATA_STREAM = auto()
        """The shell data, but converted to a utf-8 encoded string"""

        BYTES_DATA_STREAM = auto()
        """The shell data as raw bytes"""

    def __init__(self):
        super().__init__()

        # Open a pseudo TTY to control the interactive session.
        # Make it non-blocking.
        self._master, self._slave = pty.openpty()
        fl = fcntl.fcntl(self._master, fcntl.F_GETFL)
        fcntl.fcntl(self._master, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        self._process = subprocess.Popen(
            ["bash", "-i"],
            preexec_fn=os.setsid,
            stdin=self._slave,
            stdout=self._slave,
            stderr=self._slave,
        )

        # Start the shell and thread to pull data from it.
        self._running = True
        self._extraction_thread = Thread(
            name=f"Thread({self})", target=self._background, daemon=True
        )
        self._extraction_thread.start()

        # Keep track of all data sent thus far, so that after resizing the
        # state can be recovered.
        self.data_history = ""
        self.data_history_lock = RLock()

    def subscribe(self, topic, subscriber):
        # TODO: Do I want to keep this method? With longer logs it can lock up
        #       the system...
        with self.data_history_lock:
            subscriber(self.data_history)
            super().subscribe(topic, subscriber)

    def _background(self):
        """
        Background thread running the IO between the widget and the TTY session.
        """
        while True:
            ready, _, _ = select.select([self._master], [], [])
            for stream in ready:
                value = ""
                while True:
                    try:
                        data = os.read(stream, 102400)
                    except BlockingIOError:
                        break
                    if not isinstance(data, str):
                        data = data.decode("utf8", "replace")
                    value += data

                with self.data_history_lock:
                    self.data_history += value
                    self.publish(Shell.Topic.SHELL_DATA, value)

    def write(self, val: str):
        """Write a character to the tty"""
        os.write(self._master, val)
