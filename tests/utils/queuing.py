import re
from queue import Empty, Queue
from typing import Callable, Union


def drain_until_queue_equals(queue: Queue, value: bytes, timeout=5):
    """Drains a queue until an expected value is reached, or the queue
    times out."""
    _drain_until(queue, lambda retrieved: retrieved == value, timeout=timeout)


def drain_until_output_matches_regex(
    queue: Queue, regex: str, timeout=5
) -> Union[bytes, str]:
    """Drains a queue until the queues contactenated output matches a regex"""

    def check_regex(retrieved):
        if retrieved is None:
            return False
        return bool(re.match(regex, retrieved))

    return _drain_until(queue, check_regex, timeout=timeout)


def _drain_until(
    queue, drain_until: Callable[[bytes], bool], timeout
) -> Union[bytes, str]:
    """Drain a queue until a callable returns True
    :raises: Empty
    """
    retrieved = None
    while not drain_until(retrieved):
        try:
            new_value = queue.get(timeout=timeout)

            # This allows supporting both bytes and string datatypes
            if retrieved is None:
                retrieved = new_value
            else:
                retrieved += new_value
        except Empty:
            msg = (
                f"The queue never retrieved the expected value, "
                f"instead {retrieved} was retrieved before timing out. "
            )
            raise AssertionError(msg)
    return retrieved
