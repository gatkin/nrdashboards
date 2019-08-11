"""Model defintions."""
from enum import Enum, unique
from typing import Optional, List

import attr


class NrDashException(Exception):
    """Base class for all application-specific exceptions."""


class InvalidExtendingConditionException(NrDashException):
    """Invalid extending condition exception."""


class InvalidOutputConfigurationException(NrDashException):
    """Invalid output selection configuration exception."""


class InvalidQueryConfigurationException(NrDashException):
    """Invalid query configuration exception."""


class InvalidWidgetVisualizationException(NrDashException):
    """Invalid widget visualization exception."""


class InvalidWidgetConfigurationException(NrDashException):
    """Invalid widget configuration exception."""


class NewRelicApiException(NrDashException):
    """New Relic API exception."""


@unique
class WidgetVisualization(Enum):
    """Specifices the visualization type to use for a widget."""

    BILLBOARD = "billboard"
    GAUGE = "gauge"
    BILLBOARD_COMPARISON = "billboard_comparison"
    FACET_BAR_CHART = "facet_bar_chart"
    FACETED_LINE_CHART = "faceted_line_chart"
    FACET_PIE_CHART = "facet_pie_chart"
    FACET_TABLE = "facet_table"
    FACETED_AREA_CHART = "faceted_area_chart"
    HEATMAP = "heatmap"
    ATTRIBUTE_SHEET = "attribute_sheet"
    SINGLE_EVENT = "single_event"
    HISTOGRAM = "histogram"
    FUNNEL = "funnel"
    RAW_JSON = "raw_json"
    EVENT_FEED = "event_feed"
    EVENT_TABLE = "event_table"
    UNIQUES_LIST = "uniques_list"
    LINE_CHART = "line_chart"
    COMPARISON_LINE_CHART = "comparison_line_chart"
    MARKDOWN = "markdown"
    METRIC_LINE_CHART = "metric_line_chart"
    LIST = "list"

    @staticmethod
    def from_str(str_value: str):
        """Convert a string value to an enum value."""
        try:
            return WidgetVisualization[str_value.upper()]
        except KeyError:
            raise InvalidWidgetVisualizationException(str_value)


@attr.s(frozen=True)
class QueryCondition:
    """A query condition."""

    name: str = attr.ib()
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
    visualization: WidgetVisualization = attr.ib()
    nrql: Optional[str] = attr.ib(default=None)


@attr.s(frozen=True)
class ComponentizedQuery:
    """An NRQL query defined with several query components."""

    event: str = attr.ib()
    output: QueryOutputSelection = attr.ib()
    display: QueryDisplay = attr.ib()
    condition: Optional[QueryCondition] = attr.ib(default=None)

    def to_nrql(self) -> str:
        """Convert a query into a raw NRQL query string."""
        if self.display.nrql:
            display_nrql = f" {self.display.nrql}"
        else:
            display_nrql = ""

        if self.condition:
            condition_nrql = f" WHERE {self.condition.nrql}"
        else:
            condition_nrql = ""

        return f"{self.output.nrql} FROM {self.event}{condition_nrql}{display_nrql}"


@attr.s(frozen=True)
class Query:
    """An NRQL query."""

    name: str = attr.ib()
    title: str = attr.ib()
    nrql: str = attr.ib()
    visualization: WidgetVisualization = attr.ib()
    notes: Optional[str] = attr.ib(default=None)


@attr.s(frozen=True)
class Widget:
    """A widget that is placed on a single dashboard."""

    title: str = attr.ib()
    query: str = attr.ib()
    visualization: WidgetVisualization = attr.ib()
    row: int = attr.ib()
    column: int = attr.ib()
    width: int = attr.ib()
    height: int = attr.ib()
    notes: Optional[str] = attr.ib(default=None)


@attr.s(frozen=True)
class Dashboard:
    """A New Relic dashboard."""

    name: str = attr.ib()
    title: str = attr.ib()
    widgets: List[Widget] = attr.ib()
