from unittest.mock import MagicMock

import pytest
from asciimatics.strings import ColouredText
from asciimatics.widgets import Widget

from groklog.ui.filter_viewer import FilterViewer


@pytest.fixture
def filter_viewer():
    class MockFilter(MagicMock):
        pass

    class MockCanvas:
        unicode_aware = False

    class MockFrame:
        canvas = MockCanvas()

    widget = FilterViewer(filter=MockFilter(), height=Widget.FILL_FRAME)
    widget.register_frame(MockFrame())
    widget.set_layout(x=0, y=0, offset=10, w=100, h=200)

    yield widget


def test_add_lines(filter_viewer):
    # Test initial values match what's expected
    assert filter_viewer._value == [
        ColouredText("", filter_viewer._parser, colour=None)
    ]
    assert filter_viewer._reflowed_text_cache == [(filter_viewer._value[0], 0, 0)]

    # Feed 3 lines into the system
    new_lines_1 = "line1\nline2\nline3\n"
    add_and_consume_stream(new_lines_1, filter_viewer)

    # Verify they were added to the _reflowed_text_cache
    assert len(filter_viewer._value) == 4
    assert len(filter_viewer._reflowed_text_cache) == 4
    for i, reflowed in enumerate(filter_viewer._reflowed_text_cache):
        assert filter_viewer._value[i] == reflowed[0]
        assert i == reflowed[1]

    # Add another few lines and confirm they were added just the same
    new_lines_2 = "line4\nline5\n"
    add_and_consume_stream(new_lines_2, filter_viewer)
    assert len(filter_viewer._value) == 6
    assert len(filter_viewer._reflowed_text_cache) == 6
    assert filter_viewer._reflowed_text_cache[5][0]._raw_text == "line5"
    for i, reflowed in enumerate(filter_viewer._reflowed_text_cache):
        assert filter_viewer._value[i] == reflowed[0]
        assert i == reflowed[1]

    # Validate reseting doesn't clear the value or text cache
    filter_viewer.reset()
    assert len(filter_viewer._value) == 6
    assert len(filter_viewer._reflowed_text_cache) == 6


def test_subscribes_nonblocking():
    """Test that FilterViewer __init__ subscribes to the filter in a non-blocking manner"""

    filter = MagicMock()

    assert filter.subscribe_with_history.call_count == 0
    viewer = FilterViewer(filter=filter, height=Widget.FILL_FRAME)
    assert filter.subscribe_with_history.call_count == 1

    assert (
        filter.subscribe_with_history.call_args[1]["blocking"] == False
    ), "The FilterViewer should subscribe in a non-blocking manner."


def add_and_consume_stream(stream: str, filter_viewer: FilterViewer):
    """Adds lines to the filter viewer as though a filter had called _add_stream and
    the UI had called update."""
    # This would be called as a callback by a ProcessNOde
    filter_viewer._add_stream(stream)

    # This would be called in the `update` function
    while filter_viewer._processed_data_queue.qsize():
        filter_viewer.add_lines(filter_viewer._processed_data_queue.get_nowait())
