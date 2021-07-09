import fcntl
import os
import pty
import select
import subprocess
from threading import Thread

from .base import ProcessNode


class ShellProcessIO(ProcessNode):
    """
    The widget will start a bash shell in the background and use a pseudo TTY to control it.  It then
    starts a thread to transfer any data between the two processes (the one running this widget and
    the bash shell).
    """

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

    def __repr__(self):
        return f"{self.__class__.__qualname__}()"

    def _background(self):
        """
        Background thread running the IO between the widget and the TTY session.
        """
        while self._running:
            ready, _, _ = select.select([self._master], [], [])
            for stream in ready:
                data_bytes = b""
                while self._running:
                    try:
                        new_bytes = os.read(stream, 102400)
                    except BlockingIOError:
                        break
                    data_bytes += new_bytes

                self._record_and_publish(data_bytes)

    def write(self, val: bytes):
        """Write a character to the tty"""
        os.write(self._master, val)

    def send_sigint(self):
        """Simulate the user sending Ctrl+C to the underlying shell"""
        self.write("\x03".encode())
