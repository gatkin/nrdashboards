"""Model defintions."""
from typing import Optional, List

import attr


WIDGET_VISUALIZATIONS = {
    "billboard",
    "gauge",
    "billboard_comparison",
    "facet_bar_chart",
    "faceted_line_chart",
    "facet_pie_chart",
    "facet_table",
    "faceted_area_chart",
    "heatmap",
    "attribute_sheet",
    "single_event",
    "histogram",
    "funnel",
    "raw_json",
    "event_feed",
    "event_table",
    "uniques_list",
    "line_chart",
    "comparison_line_chart",
    "markdown",
    "metric_line_chart",
}


class NrDashException(Exception):
    """Base class for all application-specific exceptions."""


class InvalidExtendingFilterException(NrDashException):
    """Invalid extending filter exception."""


class InvalidOutputConfigurationException(NrDashException):
    """Invalid output selection configuration exception."""


class InvalidQueryConfigurationException(NrDashException):
    """Invalid query configuration exception."""


class InvalidWidgetConfigurationException(NrDashException):
    """Invalid widget configuration exception."""


class NewRelicApiException(NrDashException):
    """New Relic API exception."""


@attr.s(frozen=True)
class QueryFilter:
    """A query filter component."""

    name: str = attr.ib()
    event: str = attr.ib()
    nrql: str = attr.ib()


@attr.s(frozen=True)
class QueryOutputSelection:
    """A query output selection component."""

    name: str = attr.ib()
    nrql: str = attr.ib()


@attr.s(frozen=True)
class QueryDisplay:
    """A query display component."""

    name: str = attr.ib()
    nrql: str = attr.ib()


@attr.s(frozen=True)
class Query:
    """An NRQL query."""

    name: str = attr.ib()
    nrql: str = attr.ib()


@attr.s(frozen=True)
class Widget:
    """A widget that can be put on multiple dashboards."""

    name: str = attr.ib()
    title: str = attr.ib()
    query: str = attr.ib()
    visualization: str = attr.ib()
    notes: Optional[str] = attr.ib(default=None)


@attr.s(frozen=True)
class DashboardWidget:
    """A widget that is placed on a single dashboard."""

    widget: Widget = attr.ib()
    row: int = attr.ib()
    column: int = attr.ib()
    width: int = attr.ib()
    height: int = attr.ib()


@attr.s(frozen=True)
class Dashboard:
    """A New Relic dashboard."""

    name: str = attr.ib()
    title: str = attr.ib()
    widgets: List[DashboardWidget] = attr.ib()
