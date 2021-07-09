from abc import ABC, abstractmethod
from enum import Enum, auto
from threading import RLock

from pubsus import PubSubMixin


class ProcessNode(ABC, PubSubMixin):
    class Topic(Enum):
        STRING_DATA_STREAM = auto()
        """The process's stdout data, but converted to a utf-8 encoded string"""

        BYTES_DATA_STREAM = auto()
        """The process's stdout data as raw bytes"""

    def __init__(self):
        super().__init__()
        self._history_lock = RLock()
        self._bytes_history: bytes = b""
        self._string_history: str = ""

    def _record_and_publish(self, data_bytes: bytes):
        """Record the data to the history and publish the bytes and string
        variants of the data."""

        data_string: str = data_bytes.decode("utf8", "replace")

        with self._history_lock:
            self._bytes_history += data_bytes
            self._string_history += data_string

            self.publish(self.Topic.STRING_DATA_STREAM, data_string)
            self.publish(self.Topic.BYTES_DATA_STREAM, data_bytes)

    def subscribe(self, topic, subscriber):
        """When subscribing to a process node, the subscriber should get
        access to the full data history of the process."""

        with self._history_lock:
            # If any history has been writte
            if len(self._string_history):
                if topic is self.Topic.STRING_DATA_STREAM:
                    subscriber(self._string_history)
                elif topic is self.Topic.BYTES_DATA_STREAM:
                    subscriber(self._bytes_history)
            super().subscribe(topic, subscriber)

    @abstractmethod
    def write(self, val: bytes):
        pass

    def close(self, timeout=None):
        """Close all child processes and threads"""
        self._running = False
        self._process.kill()
        self._extraction_thread.join(timeout)
        self._process.wait(timeout)
