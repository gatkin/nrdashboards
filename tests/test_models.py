"""Test model defintions and methods."""
import pytest

from nrdash import models


@pytest.mark.parametrize(
    "str_value, expected",
    [(value.value, value) for value in models.WidgetVisualization.__members__.values()],
)
def test_widget_visualization_from_string(str_value, expected):
    actual = models.WidgetVisualization.from_str(str_value)
    assert expected == actual


def test_invalid_widget_visualization_string():
    with pytest.raises(models.InvalidWidgetVisualizationException):
        models.WidgetVisualization.from_str("invalid")


def test_query_to_nrql_display_and_condition():
    query = _create_query(
        event="Transactions",
        condition=_create_condition("StatusCode = 200"),
        output=_create_output_selection("SELECT COUNT(*)"),
        display=_create_display("TIMESERIES"),
    )

    expected = "SELECT COUNT(*) FROM Transactions WHERE StatusCode = 200 TIMESERIES"

    actual = query.to_nrql()

    assert expected == actual


def test_query_to_nrql_display_no_condition():
    query = _create_query(
        event="Transactions",
        condition=None,
        output=_create_output_selection("SELECT COUNT(*)"),
        display=_create_display("TIMESERIES"),
    )

    expected = "SELECT COUNT(*) FROM Transactions TIMESERIES"

    actual = query.to_nrql()

    assert expected == actual


def test_query_to_nrql_no_display_with_condition():
    query = _create_query(
        event="Transactions",
        condition=_create_condition("StatusCode = 200"),
        output=_create_output_selection("SELECT COUNT(*)"),
        display=None,
    )

    expected = "SELECT COUNT(*) FROM Transactions WHERE StatusCode = 200"

    actual = query.to_nrql()

    assert expected == actual


def test_query_to_nrql_no_display_no_condition():
    query = _create_query(
        event="Transactions",
        condition=None,
        output=_create_output_selection("SELECT COUNT(*)"),
        display=None,
    )

    expected = "SELECT COUNT(*) FROM Transactions"

    actual = query.to_nrql()

    assert expected == actual


def _create_condition(nrql):
    """Create a condition object for testing."""
    return models.QueryCondition(name="test-condition", nrql=nrql)


def _create_display(nrql=None):
    """Create a display object for testing."""
    return models.QueryDisplay(
        name="test-display",
        nrql=nrql,
        visualization=models.WidgetVisualization.EVENT_FEED,
    )


def _create_output_selection(nrql):
    """Create an output selection object for testing."""
    return models.QueryOutputSelection(name="test-output", nrql=nrql)


def _create_query(event, condition, output, display=None):
    """Create a query object for testing."""
    if not display:
        display = _create_display()

    return models.Query(
        name="test-query",
        title="Test query",
        event=event,
        output=output,
        display=display,
        condition=condition,
    )
