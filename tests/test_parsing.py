"""Test parsing YAML dashboard configurations."""
import os

import pytest
import yaml

from nrdash import models, parsing


def test_parse_empty_file():
    config = _load_test_file("empty.yml")

    assert {} == parsing.parse_conditions(config)
    assert {} == parsing.parse_output_selections(config, {})
    assert {} == parsing.parse_displays(config)
    assert {} == parsing.parse_dashboards(config)
    assert {} == parsing.parse_queries(config)


def test_parse_conditions():
    expected = {
        "base-condition": models.QueryCondition(
            name="base-condition", nrql="appName = 'MyApp'"
        ),
        "first-extended-condition": models.QueryCondition(
            name="first-extended-condition",
            nrql="(appName = 'MyApp') AND (server = 'prod1')",
        ),
        "second-extended-condition": models.QueryCondition(
            name="second-extended-condition",
            nrql="((appName = 'MyApp') AND (server = 'prod1')) AND (environment != 'test')",
        ),
        "third-extended-condition": models.QueryCondition(
            name="third-extended-condition",
            nrql="(((appName = 'MyApp') AND (server = 'prod1')) AND (environment != 'test')) OR (environment = 'qa')",
        ),
        "multiple-conditions-condition": models.QueryCondition(
            name="multiple-conditions-condition",
            nrql="(appName = 'MyApp') AND (server = 'test1') AND (status = 'error' OR status = 'failed') AND (environment = 'test')",
        ),
    }

    actual = _parse_conditions("conditions.yml")

    assert expected == actual


def test_parse_only_base_conditions():
    expected = {
        "condition-one": models.QueryCondition(
            name="condition-one", nrql="env = 'Prod'"
        ),
        "condition-two": models.QueryCondition(
            name="condition-two", nrql="server = 'Prod1'"
        ),
    }

    actual = _parse_conditions("only_base_conditions.yml")

    assert expected == actual


def test_parse_extend_only_other_conditions():
    condition_name = "extending-condition"
    expected = models.QueryCondition(
        name=condition_name, nrql="(env = 'Prod') OR (server = 'Prod1')"
    )

    actual = _parse_conditions("extend_only_other_conditions.yml")

    assert expected == actual[condition_name]


def test_parse_invalid_condition_operator():
    with pytest.raises(models.InvalidExtendingConditionException):
        _parse_conditions("invalid_condition_operator.yml")


def test_parse_extending_condition_does_not_reference_other_condition():
    with pytest.raises(models.InvalidExtendingConditionException):
        _parse_conditions(
            "conditions_extending_condition_does_not_reference_other_condition.yml"
        )


def test_parse_invalid_condition_operands():
    with pytest.raises(models.InvalidExtendingConditionException):
        _parse_conditions("invalid_condition_operands.yml")


def test_parse_unresolvable_extending_condition():
    with pytest.raises(models.InvalidExtendingConditionException):
        _parse_conditions("unresolvable_extending_condition.yml")


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
        "referenced-condition": models.QueryOutputSelection(
            name="referenced-condition",
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
            event="MyEvent",
            condition=models.QueryCondition(name="prod-events", nrql="env = 'Prod'"),
            output=models.QueryOutputSelection(
                name="total-count", nrql="SELECT COUNT(*) AS Total"
            ),
            display=models.QueryDisplay(
                name="facet-with-timeseries",
                nrql="FACET EventType LIMIT 30 TIMESERIES",
                visualization=models.WidgetVisualization.LINE_CHART,
            ),
        ),
        "no-condition-query": models.Query(
            name="no-condition-query",
            title="My Query without a Condition",
            event="MyEvent",
            output=models.QueryOutputSelection(
                name="total-count", nrql="SELECT COUNT(*) AS Total"
            ),
            display=models.QueryDisplay(
                name="facet-with-timeseries",
                nrql="FACET EventType LIMIT 30 TIMESERIES",
                visualization=models.WidgetVisualization.LINE_CHART,
            ),
        ),
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
                    query="SELECT COUNT(*) FROM transactions WHERE env = 'Prod'",
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


def test_parse_file():
    actual = parsing.parse_file(_get_test_file_path("dashboards.yml"))
    assert actual


def _assert_can_parse_dashboards(file_name, expected):
    config = _load_test_file(file_name)
    actual = parsing.parse_dashboards(config)
    assert expected == actual


def _assert_can_parse_displays(file_name, expected):
    config = _load_test_file(file_name)
    actual = parsing.parse_displays(config)
    assert expected == actual


def _assert_can_parse_output_selections(file_name, expected):
    config = _load_test_file(file_name)
    conditions = parsing.parse_conditions(config)
    actual = parsing.parse_output_selections(config, conditions)
    assert expected == actual


def _assert_can_parse_queries(file_name, expected):
    config = _load_test_file(file_name)
    actual = parsing.parse_queries(config)
    assert expected == actual


def _assert_can_parse_widgets(file_name, expected):
    config = _load_test_file(file_name)
    actual = parsing.parse_widgets(config)
    assert expected == actual


def _get_test_file_path(file_name):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(test_dir, "test_data", file_name)


def _load_test_file(file_name):
    test_file_path = _get_test_file_path(file_name)
    with open(test_file_path, "r") as test_file:
        return yaml.safe_load(test_file)


def _parse_conditions(file_name):
    config = _load_test_file(file_name)
    return parsing.parse_conditions(config)
