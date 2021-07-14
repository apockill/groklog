from abc import ABC, abstractmethod
from enum import Enum, auto
from queue import Queue
from threading import RLock
from typing import Callable, List

from pubsus import DuplicateSubscriberError, PubSubMixin


class ProcessNode(ABC, PubSubMixin):
    _READ_MAX_BYTES = 102400

    class Topic(Enum):
        STRING_DATA_STREAM = auto()
        """The process's stdout data, but converted to a utf-8 encoded string"""

        BYTES_DATA_STREAM = auto()
        """The process's stdout data as raw bytes"""

    def __init__(self, name: str, command: str):
        """
        :param name: An arbitrary unique title for this process
        :param command: The command being run in the process
        """
        super().__init__()
        self.name = name
        self.command = command
        self.children: List[ProcessNode] = []

        self._new_subscribers: Queue[Tuple[ProcessNode.Topic, Callable]] = Queue()
        """This queue contains incoming subscribers that have requested to have 
        the full history applied. This is a special case, because the callback must be
        called once with the full history. This is done in the background thread, so that
        subscribing isn't a blocking operation. """

        self._history_lock = RLock()
        self._bytes_history: bytes = b""
        self._string_history: str = ""

    def __repr__(self):
        return f"{self.__class__.__qualname__}(name='{self.name}', command='{self.command}')"

    def add_child(self, process_node: "ProcessNode"):
        """Adds and subscribes the child"""
        self.subscribe_with_history(
            ProcessNode.Topic.BYTES_DATA_STREAM, process_node.write, blocking=False
        )
        self.children.append(process_node)

    def _record_and_publish(self, data_bytes: bytes):
        """Record the data to the history and publish the bytes and string
        variants of the data."""
        # Scrub all control characters out of the string so they don't get passed on to
        # child process and kill them too

        data_string: str = data_bytes.decode("utf8", "replace")

        with self._history_lock:
            self._bytes_history += data_bytes
            self._string_history += data_string

            self.publish(self.Topic.STRING_DATA_STREAM, data_string)
            self.publish(self.Topic.BYTES_DATA_STREAM, data_bytes)

    def subscribe_with_history(
        self, topic: "ProcessNode.Topic", subscriber: Callable, *, blocking
    ):
        """This function will subscribe a subscriber to the full history that has ever
        been received by this node. The callback will occur in the background thread.
        """
        if blocking:
            self._onboard_subscriber(topic, subscriber)
        else:
            self._new_subscribers.put((topic, subscriber))

    def _onboard_new_subscribers(self):
        """Onboard any subscribers who wish to have the full history before adding more
        history.
        """

        with self._history_lock:
            while self._running and self._new_subscribers.qsize():
                self._onboard_subscriber(*self._new_subscribers.get_nowait())
                self._new_subscribers.task_done()

    def _onboard_subscriber(self, topic, subscriber):
        if self.is_subscribed(topic, subscriber):
            raise DuplicateSubscriberError("This topic/subscriber already exists!")
        with self._history_lock:
            # If any history has been written, pass it along
            if len(self._string_history):
                if topic is self.Topic.STRING_DATA_STREAM:
                    subscriber(self._string_history)
                elif topic is self.Topic.BYTES_DATA_STREAM:
                    subscriber(self._bytes_history)
                else:
                    raise ValueError("Invalid topic")
            self.subscribe(topic, subscriber)

    @abstractmethod
    def write(self, val: bytes):
        pass

    def close(self, timeout=None):
        """Close all child processes and threads"""
        self._running = False
        self._process.kill()
        self._extraction_thread.join(timeout)
        self._process.wait(timeout)

        for child in self.children:
            child.close(timeout=timeout)
