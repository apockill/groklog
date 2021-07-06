from queue import Queue

import pytest

from groklog.process_node import ShellProcessIO
from tests.utils import drain_until_output_matches_regex, drain_until_queue_equals

RE_SHELL_PREFIX = b".*\$"
"""This matches bash shells <prefix>$ before each command."""


@pytest.mark.parametrize(
    ("write_input", "expected_output"),
    [
        # Test basic
        (
            b"nonexistent command!",
            b"nonexistent: command not found\r\n",
        ),
        # Test echoing into stderr, to make sure that the shell correctly
        # captures stderr
        (
            b"echo 'stderr' 1>&2",
            b"stderr\r\n",
        ),
        # Test echoing into stdout, to make sure that the shell correctly
        # captures stderr
        (
            b"echo 'stdout'",
            b"stdout\r\n",
        ),
    ],
)
def test_input_output(write_input: str, expected_output: str, shell: ShellProcessIO):
    """Test the shell reacts in expected ways after feeding in specific
    inputs and outputs.
    """
    output = Queue()

    shell.subscribe(shell.Topic.BYTES_DATA_STREAM, output.put)

    retrieved = drain_until_output_matches_regex(
        queue=output, regex=RE_SHELL_PREFIX, timeout=10
    )
    print("GOT1", retrieved)
    for char in write_input:
        shell.write(chr(char).encode())

    drain_until_queue_equals(output, write_input)

    # Now add a newline so the command is run
    shell.write(b"\r\n")
    retrieved = drain_until_output_matches_regex(
        output, regex=b"\r\n" + expected_output + RE_SHELL_PREFIX
    )
    print("GOT2", retrieved)
