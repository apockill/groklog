from queue import Queue

import pytest

from groklog.process_node import GenericProcessIO, ShellProcessIO
from tests.utils import drain_until_queue_equals


@pytest.mark.parametrize(
    ("command", "input_bytes", "expected_output_bytes"),
    [
        # Test a big input
        ["cat", b"hello world\n" * 1000, b"hello world\n" * 1000],
        # Test a small input
        ["cat", b"hello world", b"hello world"],
        # Test grep functionality
        ["grep --line-buffered world", b"hello\nworld\n", b"world\n"],
        ["grep --line-buffered -v world", b"hello\nworld\n", b"hello\n"],
    ],
)
def test_generic_process(
    command: str, input_bytes: bytes, expected_output_bytes: bytes
):
    process = GenericProcessIO(command=command)
    output_queue = Queue()
    process.subscribe(process.Topic.BYTES_DATA_STREAM, output_queue.put)
    process.write(input_bytes)

    # Wait for results from the process
    output = b""
    drain_until_queue_equals(output_queue, expected_output_bytes)

    assert process._bytes_history == expected_output_bytes
    assert process._string_history == expected_output_bytes.decode("utf-8", "replace")
    process.close()


def test_history_is_passed():
    process = GenericProcessIO("cat")

    assert process._bytes_history == b""
    assert process._string_history == ""

    # Subscribe and assert that on subscription, if the history is empty, that
    # the subscriber isn't called
    first_subscriber = Queue()
    process.subscribe(process.Topic.BYTES_DATA_STREAM, first_subscriber.put)
    assert first_subscriber.qsize() == 0

    # Write some history down
    first_input = b"very cool input!" * 10000
    process.write(first_input)

    # Wait until the first subscriber receives the full message (or times out)
    drain_until_queue_equals(first_subscriber, first_input)

    # Now any new subscriber should get the first input upon subscription
    second_subscriber = Queue()
    process.subscribe(process.Topic.BYTES_DATA_STREAM, second_subscriber.put)
    # We specifically use get_nowait because the subscribe call should have
    # _immediately_ dumped the process history into the subscriber callable.
    second_subscriber_output = second_subscriber.get_nowait()
    assert first_subscriber.qsize() == 0
    assert second_subscriber_output == first_input

    # Now if we publish a second input, both queues should receive it.
    second_input = b"wow more cool input!" * 100
    process.write(second_input)
    drain_until_queue_equals(first_subscriber, second_input)
    drain_until_queue_equals(second_subscriber, second_input)

    # Close resources
    process.close()
