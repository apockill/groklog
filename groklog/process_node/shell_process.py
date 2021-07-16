import fcntl
import os
import pty
import select
import signal
import subprocess
from threading import Thread

from .base import ProcessNode


class ShellProcessIO(ProcessNode):
    """
    This object is a custom ProcessNode which exposes the same PubSub system, but has
    better control over reading and writing to the underlying shell than the
    GenericProcessIO process node. It also exposes a `send_sigint` function.
    """

    def __init__(self, name="Shell", command="bash -i"):
        super().__init__(name=name, command=command)

        # Open a pseudo TTY to control the interactive session.
        # Make it non-blocking.
        self._master, self._slave = pty.openpty()
        fl = fcntl.fcntl(self._master, fcntl.F_GETFL)
        fcntl.fcntl(self._master, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        self._process = subprocess.Popen(
            self.command.split(" "),
            preexec_fn=os.setsid,
            stdin=self._slave,
            stdout=self._slave,
            stderr=self._slave,
        )

        # Start the shell and thread to pull data from it.
        self._running = True
        self._extraction_thread = Thread(
            name=f"{self.name} Extractor Thread", target=self._background, daemon=True
        )
        self._extraction_thread.start()

    def _background(self):
        """
        Background thread running the IO between the widget and the TTY session.
        """
        while self._running:
            # Wait for any of the file descriptors to have data, with a 1 second timeout
            ready, _, _ = select.select([self._master], [], [], 0.1)
            self._onboard_new_subscribers()

            for stream in ready:
                data_bytes = b""
                while self._running:
                    try:
                        new_bytes = os.read(stream, self._READ_MAX_BYTES)
                    except BlockingIOError:
                        break
                    data_bytes += new_bytes

                self._record_and_publish(data_bytes)

    def write(self, val: bytes):
        """Write a character to the tty"""
        os.write(self._master, val)

    def send_sigint(self):
        """Simulate the user sending Ctrl+C to the underlying shell"""
        self.write(b"\x03")

    def close(self, timeout=None):
        """While not necessary, sending a sigint significantly speeds up the closing
        process, which is great for tests."""
        self.send_sigint()
        super().close(timeout=timeout)
