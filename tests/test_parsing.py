import os

import pytest

from nrdash import models, parsing


def test_parse_simple_base_filter():
    expected = {
        "simple_base_filter": models.QueryFilter(
            name="simple_base_filter", event="My_Event", nrql="WHERE appName = 'MyApp'"
        ),
        "first_extended_filter": models.QueryFilter(
            name="first_extended_filter",
            event="My_Event",
            nrql="WHERE appName = 'MyApp' AND server = 'prod1'",
        ),
        "second_extended_filter": models.QueryFilter(
            name="second_extended_filter",
            event="My_Event",
            nrql="WHERE appName = 'MyApp' AND server = 'prod1' AND environment != 'test'",
        ),
        "third_extended_filter": models.QueryFilter(
            name="third_extended_filter",
            event="My_Event",
            nrql="WHERE appName = 'MyApp' AND server = 'prod1' AND environment != 'test' AND environment != 'qa'",
        ),
        "event_only_filter": models.QueryFilter(
            name="event_only_filter", event="My_Event", nrql=""
        ),
        "extend_event_only_filter": models.QueryFilter(
            name="extend_event_only_filter",
            event="My_Event",
            nrql="WHERE server = 'prod2'",
        ),
    }

    _assert_can_parse_filters("filters.yml", expected)


def test_raises_exception_for_missing_extended_query():
    with pytest.raises(models.InvalidExtendingFilterException):
        _parse_test_file("missing_extended_filter.yml")


def _assert_can_parse_filters(file_name, expected):
    actual = _parse_test_file(file_name)
    assert expected == actual.filters


def _parse_test_file(file_name):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(test_dir, "test_data", file_name)
    return parsing.parse_file(test_file_path)
