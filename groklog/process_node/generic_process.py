import fcntl
import os
import shlex
import subprocess
from threading import RLock, Thread
from time import sleep

from .base import ProcessNode


class GenericProcessIO(ProcessNode):
    def __init__(self, name: str, command: str):
        super().__init__(name=name, command=command)

        self._process = subprocess.Popen(
            self.command,
            preexec_fn=os.setsid,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        # Set stdout to be nonblocking
        fd = self._process.stdout.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        # Lock while processes are piping data in
        self._input_lock = RLock()

        self._running = True
        self._extraction_thread = Thread(
            name=f"Thread({self})", daemon=True, target=self._background
        )
        self._extraction_thread.start()

    def write(self, data: bytes):
        """Input data from an upstream process"""
        if not self._running:
            return

        with self._input_lock:
            self._process.stdin.write(data)
            self._process.stdin.flush()

    def _background(self):
        while self._running:
            self._onboard_new_subscribers()

            # Read in a non-blocking fashion up to a certain number of characters.
            data_bytes = self._process.stdout.read1(self._READ_MAX_BYTES)

            if len(data_bytes) == 0:
                # Prevent a busyloop where there's no data in stdout.
                sleep(0.1)
                continue

            self._record_and_publish(data_bytes)
