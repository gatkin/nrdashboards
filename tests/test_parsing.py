import os

import pytest
import yaml

from nrdash import models, parsing


def test_parse_empty_file():
    config = _load_test_file("empty.yml")

    assert {} == parsing.parse_filters(config)
    assert {} == parsing.parse_output_selections(config)
    assert {} == parsing.parse_displays(config)
    assert {} == parsing.parse_widgets(config)
    assert {} == parsing.parse_dashboards(config)


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


def test_parse_queries():
    expected = {
        "raw-nrql": models.Query(
            name="raw-nrql", nrql="SELECT COUNT(*) FROM transactions"
        ),
        "with-filter-output": models.Query(
            name="with-filter-output",
            nrql="SELECT COUNT(*) FROM AppEvents WHERE env = 'Prod'",
        ),
        "with-filter-output-display": models.Query(
            name="with-filter-output-display",
            nrql="SELECT COUNT(*) FROM AppEvents WHERE env = 'Prod' FACET EventType LIMIT 30 TIMESERIES",
        ),
    }

    _assert_can_parse_queries("queries.yml", expected)


def test_parse_widgets():
    expected = {
        "transaction-count": models.Widget(
            name="transaction-count",
            query="SELECT COUNT(*) FROM transactions",
            title="Transaction Count",
            visualization="billboard",
        ),
        "errors": models.Widget(
            name="errors",
            title="Application Errors",
            query="SELECT COUNT(*) FROM errors",
            notes="Some notes for the dashboard",
            visualization="billboard",
        ),
    }

    _assert_can_parse_widgets("widgets.yml", expected)


def test_parse_widgets():
    expected = {
        "dashboard-one": models.Dashboard(
            name="dashboard-one",
            title="Dashboard 1",
            widgets=[
                models.DashboardWidget(
                    widget=models.Widget(
                        name="transaction-count",
                        query="SELECT COUNT(*) FROM transactions",
                        title="Transaction Count",
                        visualization="billboard",
                    ),
                    row=1,
                    column=1,
                    width=1,
                    height=1,
                ),
                models.DashboardWidget(
                    widget=models.Widget(
                        name="errors",
                        title="Application Errors",
                        query="SELECT COUNT(*) FROM errors",
                        notes="Some notes for the dashboard",
                        visualization="billboard",
                    ),
                    row=1,
                    column=2,
                    width=2,
                    height=1,
                ),
            ],
        ),
        "dashboard-two": models.Dashboard(
            name="dashboard-two",
            title="Dashboard 2",
            widgets=[
                models.DashboardWidget(
                    widget=models.Widget(
                        name="transaction-count",
                        query="SELECT COUNT(*) FROM transactions",
                        title="Transaction Count",
                        visualization="billboard",
                    ),
                    row=1,
                    column=1,
                    width=3,
                    height=3,
                )
            ],
        ),
    }

    _assert_can_parse_dashboards("dashboards.yml", expected)


def test_raises_exception_for_missing_extended_query():
    with pytest.raises(models.InvalidExtendingFilterException):
        config = _load_test_file("missing_extended_filter.yml")
        parsing.parse_filters(config)


def _assert_can_parse_dashboards(file_name, expected):
    config = _load_test_file(file_name)
    actual = parsing.parse_dashboards(config)
    assert expected == actual


def _assert_can_parse_displays(file_name, expected):
    config = _load_test_file(file_name)
    actual = parsing.parse_displays(config)
    assert expected == actual


def _assert_can_parse_filters(file_name, expected):
    config = _load_test_file(file_name)
    actual = parsing.parse_filters(config)
    assert expected == actual


def _assert_can_parse_output_selections(file_name, expected):
    config = _load_test_file(file_name)
    actual = parsing.parse_output_selections(config)
    assert expected == actual


def _assert_can_parse_queries(file_name, expected):
    config = _load_test_file(file_name)
    actual = parsing.parse_queries(config)
    assert expected == actual


def _assert_can_parse_widgets(file_name, expected):
    config = _load_test_file(file_name)
    actual = parsing.parse_widgets(config)
    assert expected == actual


def _load_test_file(file_name):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(test_dir, "test_data", file_name)
    with open(test_file_path, "r") as test_file:
        return yaml.safe_load(test_file)
