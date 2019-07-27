import os

import pytest
import yaml

from nrdash import models, parsing


def test_parse_empty_file():
    config = _load_test_file("empty.yml")

    assert {} == parsing.parse_filters(config)
    assert {} == parsing.parse_output_selections(config, {})
    assert {} == parsing.parse_displays(config)
    assert {} == parsing.parse_dashboards(config)


def test_parse_filters():
    expected = {
        "base-filter": models.QueryFilter(
            name="base-filter", event="MyEvent", nrql="appName = 'MyApp'"
        ),
        "first-extended-filter": models.QueryFilter(
            name="first-extended-filter",
            event="MyEvent",
            nrql="(appName = 'MyApp') AND (server = 'prod1')",
        ),
        "second-extended-filter": models.QueryFilter(
            name="second-extended-filter",
            event="MyEvent",
            nrql="((appName = 'MyApp') AND (server = 'prod1')) AND (environment != 'test')",
        ),
        "third-extended-filter": models.QueryFilter(
            name="third-extended-filter",
            event="MyEvent",
            nrql="(((appName = 'MyApp') AND (server = 'prod1')) AND (environment != 'test')) OR (environment = 'qa')",
        ),
        "event-only-filter": models.QueryFilter(
            name="event-only-filter", event="MyEvent", nrql=None
        ),
        "multiple-conditions-filter": models.QueryFilter(
            name="multiple-conditions-filter",
            event="MyEvent",
            nrql="(server = 'test1') AND (status = 'error' OR status = 'failed') AND (environment = 'test')",
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
        "referenced-filter": models.QueryOutputSelection(
            name="referenced-filter",
            nrql="SELECT FILTER(LATEST(timestamp), WHERE env = 'prod')",
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
            name="facet-feed-type",
            nrql="FACET Feed_Type LIMIT 30",
            visualization=models.WidgetVisualization.FACET_TABLE,
        ),
        "time-series-by-feed-type": models.QueryDisplay(
            name="time-series-by-feed-type",
            nrql="TIMESERIES FACET Feed_Type",
            visualization=models.WidgetVisualization.LINE_CHART,
        ),
        "compare-with-one-week-ago": models.QueryDisplay(
            name="compare-with-one-week-ago",
            nrql="COMPARE WITH 1 WEEK AGO",
            visualization=models.WidgetVisualization.BILLBOARD_COMPARISON,
        ),
        "just-a-billboard": models.QueryDisplay(
            name="just-a-billboard", visualization=models.WidgetVisualization.BILLBOARD
        ),
    }

    _assert_can_parse_displays("displays.yml", expected)


def test_parse_queries():
    expected = {
        "my-query": models.Query(
            name="my-query",
            title="My Query",
            notes="Notes about my query",
            query_filter=models.QueryFilter(
                name="prod-events", event="AppEvents", nrql="(env = 'Prod')"
            ),
            output=models.QueryOutputSelection(
                name="total-count", nrql="SELECT COUNT(*) AS Total"
            ),
            display=models.QueryDisplay(
                name="facet-with-timeseries",
                nrql="FACET EventType LIMIT 30 TIMESERIES",
                visualization=models.WidgetVisualization.LINE_CHART,
            ),
        )
    }

    _assert_can_parse_queries("queries.yml", expected)


def test_parse_dashboards():
    expected = {
        "my-dashboard": models.Dashboard(
            name="my-dashboard",
            title="My Dashboard",
            widgets=[
                models.Widget(
                    title="Transaction Count",
                    query="SELECT COUNT(*) FROM transactions",
                    visualization=models.WidgetVisualization.BILLBOARD,
                    row=1,
                    column=1,
                    width=1,
                    height=1,
                )
            ],
        )
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
    filters = parsing.parse_filters(config)
    actual = parsing.parse_output_selections(config, filters)
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
