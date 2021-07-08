import pytest

from groklog.filter_model import (
    ROOT_FILTER_NAME,
    DuplicateFilterError,
    Filter,
    FilterModel,
    FilterNotFoundError,
)


def test_instantiation_registers_root_filter(mock_shell):
    filter_model = FilterModel(shell=mock_shell)
    assert len(filter_model._filters) == 1
    filter = filter_model._filters[ROOT_FILTER_NAME]
    assert isinstance(filter, Filter)
    assert filter.name == ROOT_FILTER_NAME
    assert filter.command == ""


def test_no_parent_raises_error(mock_shell):
    """Test creating a filter without a parent that isn't a ShellProcessIO"""
    filter_model = FilterModel(shell=mock_shell)
    with pytest.raises(RuntimeError):
        filter_model.create_filter("Cool filter", command="cat", parent=None)


def test_duplicate_filter_name_raises_error(mock_shell):
    """Test creating a filter with the same name as another filter"""
    filter_model = FilterModel(shell=mock_shell)
    filter_model.create_filter(
        "Cool filter", command="cat", parent=filter_model.root_filter
    )
    with pytest.raises(DuplicateFilterError):
        filter_model.create_filter(
            name="Cool filter",
            command="irrelevant",
            parent=filter_model.root_filter,
        )


def test_create_filter(mock_shell):
    """Test the failure cases when creating a filter"""
    filter_model = FilterModel(shell=mock_shell)
    new_filter = filter_model.create_filter(
        name="Cool filter",
        command="grep -k",
        parent=filter_model.root_filter,
    )
    assert filter_model.get_filter("Cool filter") is new_filter
    assert new_filter.name == "Cool filter"
    assert new_filter.command == "grep -k"
    assert new_filter.parent is filter_model.root_filter
    assert filter_model._filters[new_filter.name] is new_filter
    assert len(filter_model._filters) == 2


def test_get_filter(mock_shell):
    filter_model = FilterModel(shell=mock_shell)
    assert filter_model.root_filter is filter_model._filters[ROOT_FILTER_NAME]

    with pytest.raises(FilterNotFoundError):
        filter_model.get_filter("nonexistent filter name")
