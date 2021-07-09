import pytest

from groklog.filter_manager import (
    ROOT_FILTER_NAME,
    DuplicateFilterError,
    Filter,
    FilterNotFoundError,
)


def test_instantiation_registers_root_filter(filter_manager):
    assert len(filter_manager._filters) == 1
    filter = filter_manager._filters[ROOT_FILTER_NAME]
    assert isinstance(filter, Filter)
    assert filter.name == ROOT_FILTER_NAME
    assert filter.command == ""


def test_duplicate_filter_name_raises_error(filter_manager):
    """Test creating a filter with the same name as another filter"""
    filter_manager.create_filter(
        "Cool filter", command="cat", parent=filter_manager.root_filter
    )
    with pytest.raises(DuplicateFilterError):
        filter_manager.create_filter(
            name="Cool filter",
            command="irrelevant",
            parent=filter_manager.root_filter,
        )


def test_create_filter(filter_manager):
    """Test the failure cases when creating a filter"""
    new_filter = filter_manager.create_filter(
        name="Cool filter",
        command="grep -k",
        parent=filter_manager.root_filter,
    )
    assert filter_manager.get_filter("Cool filter") is new_filter
    assert new_filter.name == "Cool filter"
    assert new_filter.command == "grep -k"
    assert filter_manager.root_filter.children == [new_filter]
    assert filter_manager._filters[new_filter.name] is new_filter
    assert len(filter_manager._filters) == 2


def test_get_filter(filter_manager):
    assert filter_manager.root_filter is filter_manager._filters[ROOT_FILTER_NAME]
    assert (
        filter_manager.get_filter(ROOT_FILTER_NAME)
        is filter_manager._filters[ROOT_FILTER_NAME]
    )

    with pytest.raises(FilterNotFoundError):
        filter_manager.get_filter("nonexistent filter name")


def test_iteration(filter_manager):
    filters = [filter_manager.root_filter]
    filters += [
        filter_manager.create_filter(
            name=f"cool_filter {i}",
            command="cat",
            parent=filter_manager.root_filter,
        )
        for i in range(5)
    ]

    assert list(filter_manager) == filters
