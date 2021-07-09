import pytest

from groklog.filter_manager import FilterManager
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
def filter_manager(shell):
    manager = FilterManager(shell=shell)
    yield manager
    manager.close()
