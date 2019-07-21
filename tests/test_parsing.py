import os

import pytest

from nrdash import models, parsing


def test_parse_empty_file():
    expected = models.DashboardConfiguration(
        filters={}, output_selections={}, displays={}
    )

    actual = _parse_test_file("empty.yml")

    assert expected == actual


def test_parse_filters():
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


def test_parse_output_selections():
    expected = {
        "latest-timestamp-raw-nrql": models.QueryOutputSelection(
            name="latest-timestamp-raw-nrql", nrql="SELECT LATEST(timestamp)"
        ),
        "error-percentage-singleton-list": models.QueryOutputSelection(
            name="error-percentage-singleton-list",
            nrql="SELECT PERCENTAGE(COUNT(*), WHERE status != 'Success') AS `Error Rate`",
        ),
        "latest-success-dict": models.QueryOutputSelection(
            name="latest-success-dict",
            nrql="SELECT FILTER(LATEST(timestamp), WHERE status = 'Success')",
        ),
        "mixed": models.QueryOutputSelection(
            name="mixed",
            nrql="SELECT PERCENTAGE(COUNT(*), WHERE status != 'Success'), LATEST(timestamp) AS `Latest Event`, FILTER(LATEST(timestamp), WHERE status = 'Success') AS `Latest Success`",
        ),
    }

    _assert_can_parse_output_selections("output_selections.yml", expected)


def test_parse_displays():
    expected = {
        "facet-feed-type": models.QueryDisplay(
            name="facet-feed-type", nrql="FACET Feed_Type LIMIT 30"
        ),
        "time-series-by-feed-type": models.QueryDisplay(
            name="time-series-by-feed-type", nrql="TIMESERIES FACET Feed_Type"
        ),
        "compare-with-one-week-ago": models.QueryDisplay(
            name="compare-with-one-week-ago", nrql="COMPARE WITH 1 WEEK AGO"
        ),
    }

    _assert_can_parse_displays("displays.yml", expected)


def test_raises_exception_for_missing_extended_query():
    with pytest.raises(models.InvalidExtendingFilterException):
        _parse_test_file("missing_extended_filter.yml")


def _assert_can_parse_displays(file_name, expected):
    actual = _parse_test_file(file_name)
    assert expected == actual.displays


def _assert_can_parse_filters(file_name, expected):
    actual = _parse_test_file(file_name)
    assert expected == actual.filters


def _assert_can_parse_output_selections(file_name, expected):
    actual = _parse_test_file(file_name)
    assert expected == actual.output_selections


def _parse_test_file(file_name):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(test_dir, "test_data", file_name)
    return parsing.parse_file(test_file_path)
