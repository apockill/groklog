from queue import Queue

from tests.utils import (
    RE_SHELL_PREFIX,
    drain_until_output_matches_regex,
    drain_until_queue_equals,
)

"""These are smoke tests to sus out any issues in the pubsub/IPC system"""


def test_linear_tree(filter_manager):
    """Test robustness by creating a long chain of "cat" processes and publishing on
    one end and listening on the other.
    """
    last_filter = filter_manager.root_filter

    # Wait for the shell to start up properly
    shell_output = Queue()
    last_filter.subscribe(last_filter.Topic.BYTES_DATA_STREAM, shell_output.put)
    drain_until_output_matches_regex(shell_output, RE_SHELL_PREFIX, timeout=5)

    for i in range(10):
        last_filter = filter_manager.create_filter(
            name=f"Cat {i}",
            command="cat",
            parent=last_filter,
        )

    last_filter_output = Queue()
    last_filter.subscribe(last_filter.Topic.BYTES_DATA_STREAM, last_filter_output.put)
    # last_filter.subscribe(last_filter.Topic.BYTES_DATA_STREAM, output)

    drain_until_output_matches_regex(last_filter_output, RE_SHELL_PREFIX, timeout=5)

    filter_manager.root_filter.write(b"test" * 5)
    drain_until_queue_equals(last_filter_output, b"test" * 5, timeout=5)
