"""Parses input configuration files."""
from typing import Dict

import attr
import yaml

from .models import (
    Dashboard,
    DahsboardWidget,
    InvalidExtendingFilterException,
    InvalidOutputConfigurationException,
    InvalidQueryConfigurationException,
    InvalidWidgetConfigurationException,
    Query,
    QueryDisplay,
    QueryFilter,
    QueryOutputSelection,
    Widget,
)


@attr.s(frozen=True)
class _ExtendingQueryFilter:
    """A query filter that extends another query filter."""

    name: str = attr.ib()
    extension_nrql: str = attr.ib()
    extended_filter: str = attr.ib()


def parse_dashboards(config: Dict) -> Dict[str, Dashboard]:
    """Parse dashboards from configuration."""
    if "dashboards" not in config:
        return {}

    dashboard_configs = config["dashboards"]
    widgets = parse_widgets(config)

    dashboards = {}
    for name, dashboard_config in dashboard_configs.items():
        dashboard_widgets = []
        for widget_config in dashboard_config["widgets"]:
            dashboard_widgets.append(
                DahsboardWidget(
                    widget=widgets[widget_config["widget"]],
                    row=widget_config["row"],
                    column=widget_config["column"],
                    width=widget_config["width"],
                    height=widget_config["height"],
                )
            )

        dashboards[name] = Dashboard(
            name=name, title=dashboard_config["title"], widgets=dashboard_widgets
        )

    return dashboards


def parse_displays(config: Dict) -> Dict[str, QueryDisplay]:
    """Parse display options from configuration."""
    if "displays" not in config:
        return {}

    display_configs = config["displays"]
    displays = {}
    for name, display_config in display_configs.items():
        displays[name] = QueryDisplay(name=name, nrql=display_config)

    return displays


def parse_file(file_path: str) -> Dict[str, Query]:
    """Parse a dashboard configuration file."""
    with open(file_path, "r") as config_file:
        config = yaml.safe_load(config_file)

    return parse_queries(config)


def parse_filters(config: Dict) -> Dict[str, QueryFilter]:
    """Parse filters from configuration."""
    if "filters" not in config:
        return {}

    filter_configs = config["filters"]

    base_filters = {}
    extending_filters = {}
    for name, filter_config in filter_configs.items():
        if "extend" in filter_config:
            extending_filters[name] = _ExtendingQueryFilter(
                name=name,
                extension_nrql=filter_config["extend"]["with"],
                extended_filter=filter_config["extend"]["filter"],
            )
        else:
            base_filters[name] = QueryFilter(
                name=name,
                nrql=filter_config.get("nrql", ""),
                event=filter_config["event"],
            )

    return _build_extended_filters(base_filters, extending_filters)


def parse_output_selections(config: Dict) -> Dict[str, QueryOutputSelection]:
    """Parse output selections from configuration."""
    if "output-selections" not in config:
        return {}

    output_configs = config["output-selections"]

    output_selections = {}
    for name, output_config in output_configs.items():
        if isinstance(output_config, str):
            # Raw NRQL
            output_selections[name] = QueryOutputSelection(
                name=name, nrql=f"SELECT {output_config}"
            )
        elif isinstance(output_config, list):
            nrql_components = [
                _parse_output_selection_nrql_component(component_config)
                for component_config in output_config
            ]

            output_selections[name] = QueryOutputSelection(
                name=name, nrql=f"SELECT {', '.join(nrql_components)}"
            )
        elif isinstance(output_config, dict):
            output_selections[name] = QueryOutputSelection(
                name=name,
                nrql=f"SELECT {_parse_output_selection_nrql_component(output_config)}",
            )
        else:
            raise InvalidOutputConfigurationException(output_config)

    return output_selections


def parse_queries(config: Dict) -> Dict[str, Query]:
    """Parse queries from configuration."""
    if "queries" not in config:
        return {}

    query_configs = config["queries"]
    filters = parse_filters(config)
    output_selections = parse_output_selections(config)
    displays = parse_displays(config)

    queries = {}
    for name, query_config in query_configs.items():
        if isinstance(query_config, str):
            # Raw NRQL
            queries[name] = Query(name=name, nrql=query_config)
        elif isinstance(query_config, dict):
            queries[name] = _parse_query_config(
                name, query_config, filters, output_selections, displays
            )
        else:
            raise InvalidOutputConfigurationException(f"{name}: {query_config}")

    return queries


def parse_widgets(config: Dict) -> Dict[str, Widget]:
    """Parse dashboard widgets from configuration."""
    if "widgets" not in config:
        return {}

    widget_configs = config["widgets"]
    queries = parse_queries(config)

    widgets = {}
    for name, widget_config in widget_configs.items():
        query_name = widget_config["query"]
        query = queries.get(query_name)
        if not query:
            raise InvalidWidgetConfigurationException(
                f"Invalid query {query_name} specified for widget {name}"
            )

        widgets[name] = Widget(
            name=name,
            title=widget_config["title"],
            query=query.nrql,
            notes=widget_config.get("notes"),
        )

    return widgets


def _build_extended_filters(base_filters, extending_filters):
    """Convert extended filters into base filters."""
    filters_to_resolve = len(extending_filters)
    while filters_to_resolve > 0:
        unresolved_filters = [
            extending_filter
            for filter_name, extending_filter in extending_filters.items()
            if filter_name not in base_filters
        ]

        resolvable_filters = [
            extending_filter
            for extending_filter in unresolved_filters
            if extending_filter.extended_filter in base_filters
        ]

        if not resolvable_filters:
            unresolved_names = ",".join(
                (extending_filter.name for extending_filter in unresolved_filters)
            )
            raise InvalidExtendingFilterException(
                f"Extending filters do not reference valid filters and cannot be resolved: {unresolved_names}"
            )

        for extending_filter in resolvable_filters:
            extended_base_filter = base_filters[extending_filter.extended_filter]
            full_nrql = (
                f"{extended_base_filter.nrql} {extending_filter.extension_nrql}".strip()
            )

            base_filters[extending_filter.name] = QueryFilter(
                name=extending_filter.name,
                nrql=full_nrql,
                event=extended_base_filter.event,
            )

        filters_to_resolve -= len(resolvable_filters)

    return base_filters


def _create_filtered_output_selection_nrql(output_function, output_config):
    """Create a filtered output selection."""
    function = output_config["function"]
    function_filter = output_config["condition"]
    label = output_config.get("label")
    if label:
        label_nrql = f" AS `{label}`"
    else:
        label_nrql = ""

    return f"{output_function}({function}, {function_filter}){label_nrql}"


def _parse_output_selection_nrql_component(output_config):
    """Parse an output selection configuration dictionary."""
    if isinstance(output_config, str):
        # Raw NRQL
        return output_config

    if not isinstance(output_config, dict):
        raise InvalidOutputConfigurationException(output_config)

    if "filter" in output_config:
        return _create_filtered_output_selection_nrql("FILTER", output_config["filter"])

    if "percentage" in output_config:
        return _create_filtered_output_selection_nrql(
            "PERCENTAGE", output_config["percentage"]
        )

    raise InvalidOutputConfigurationException(output_config)


def _parse_query_config(query_name, query_config, filters, output_selections, displays):
    """Parse a query configuration."""
    if "filter" not in query_config:
        raise InvalidQueryConfigurationException(
            f"Filter required for query {query_name}"
        )

    if "output" not in query_config:
        raise InvalidQueryConfigurationException(
            f"Output required for query {query_name}"
        )

    filter_name = query_config["filter"]
    query_filter = filters.get(filter_name)
    if not query_filter:
        raise InvalidQueryConfigurationException(
            f"Invalid filter {filter_name} specified for query {query_name}"
        )

    output_name = query_config["output"]
    query_output = output_selections.get(output_name)
    if not query_output:
        raise InvalidQueryConfigurationException(
            f"Invalid output selection {output_name} specified for query {query_name}"
        )

    query_display_nrql = ""
    display_name = query_config.get("display")
    if display_name:
        # Query display is optional
        display = displays.get(display_name)
        if not display:
            raise InvalidQueryConfigurationException(
                f"Invalid display {display_name} specified for query {query_name}"
            )

        query_display_nrql = f" {display.nrql}"

    query_nrql = f"{query_output.nrql} FROM {query_filter.event} {query_filter.nrql}{query_display_nrql}"

    return Query(name=query_name, nrql=query_nrql)
