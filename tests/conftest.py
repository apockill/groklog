import pytest

from groklog.process_node import ShellProcessIO
from tests import utils


@pytest.fixture(autouse=True, scope="function")
def every_test_teardown():
    """Validate all threads and processes are shut down after each test"""
    yield
    utils.verify_all_threads_closed()
    utils.verify_all_child_processes_closed()


@pytest.fixture()
def shell():
    shell = ShellProcessIO()
    yield shell
    shell.close(timeout=10)


@pytest.fixture()
def mock_shell():
    class ShellMock(ShellProcessIO):
        def __init__(self):
            # Don't call the parent class here, to avoid starting subprocesses
            pass

    yield ShellMock()
