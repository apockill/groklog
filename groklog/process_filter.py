import subprocess
from enum import Enum, auto
from threading import RLock, Thread

from pubsus import PubSubMixin


class ProcessFilter(PubSubMixin):
    class Topic(Enum):
        STRING_DATA_STREAM = auto()
        BYTES_DATA_STREAM = auto()

    def __init__(self, command: str):
        super().__init__()

        self._process = subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        # Lock while processes are piping data in
        self._input_lock = RLock()

        self._running = True
        self._extraction_thread = Thread(daemon=True, target=self._background)
        self._extraction_thread.start()

    def write(self, data: bytes):
        """Input data from an upstream process"""
        with self._input_lock:
            self._process.stdin.write(data)
            self._process.stdin.flush()

    def _background(self):
        while self._running:
            data_bytes = self._process.stdout.read1(102400)

            if len(data_bytes) == 0:
                continue

            data_string = data_bytes.decode("utf8", "replace")
            self.publish(ProcessFilter.Topic.STRING_DATA_STREAM, data_string)
            self.publish(ProcessFilter.Topic.BYTES_DATA_STREAM, data_bytes)

    def close(self):
        """Close all child processes and threads"""
        self._running = False
        self._process.terminate()
        self._extraction_thread.join()
        self._process.wait()
