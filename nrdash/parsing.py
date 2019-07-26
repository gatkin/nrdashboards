"""Parses input configuration files."""
from typing import Dict

import attr
import yaml

from .models import (
    Dashboard,
    Widget,
    InvalidExtendingFilterException,
    InvalidOutputConfigurationException,
    InvalidQueryConfigurationException,
    InvalidWidgetConfigurationException,
    Query,
    QueryDisplay,
    QueryFilter,
    QueryOutputSelection,
    WidgetVisualization,
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
    queries = parse_queries(config)

    dashboards = {}
    for name, dashboard_config in dashboard_configs.items():
        widgets = []
        for widget_config in dashboard_config["widgets"]:
            widgets.append(_parse_widget(widget_config, name, queries))

        dashboards[name] = Dashboard(
            name=name, title=dashboard_config["title"], widgets=widgets
        )

    return dashboards


def parse_displays(config: Dict) -> Dict[str, QueryDisplay]:
    """Parse display options from configuration."""
    if "displays" not in config:
        return {}

    display_configs = config["displays"]
    displays = {}
    for name, display_config in display_configs.items():
        displays[name] = QueryDisplay(
            name=name,
            nrql=display_config.get("nrql"),
            visualization=WidgetVisualization.from_str(display_config["visualization"]),
        )

    return displays


def parse_file(file_path: str) -> Dict[str, Dashboard]:
    """Parse a dashboard configuration file."""
    with open(file_path, "r") as config_file:
        config = yaml.safe_load(config_file)

    return parse_dashboards(config)


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


def parse_output_selections(
    config: Dict, filters: Dict[str, QueryFilter]
) -> Dict[str, QueryOutputSelection]:
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
                _parse_output_selection_nrql_component(component_config, filters)
                for component_config in output_config
            ]

            output_selections[name] = QueryOutputSelection(
                name=name, nrql=f"SELECT {', '.join(nrql_components)}"
            )
        elif isinstance(output_config, dict):
            output_selections[name] = QueryOutputSelection(
                name=name,
                nrql=f"SELECT {_parse_output_selection_nrql_component(output_config, filters)}",
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
    output_selections = parse_output_selections(config, filters)
    displays = parse_displays(config)

    queries = {}
    for name, query_config in query_configs.items():
        queries[name] = _parse_query_config(
            name, query_config, filters, output_selections, displays
        )

    return queries


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


def _create_filtered_output_selection_nrql(output_function, output_config, filters):
    """Create a filtered output selection."""
    function = output_config["function"]
    label = output_config.get("label")
    if label:
        label_nrql = f" AS `{label}`"
    else:
        label_nrql = ""

    function_filter = output_config["condition"]
    if function_filter in filters:
        condition_nrql = filters[function_filter].nrql
    else:
        condition_nrql = function_filter

    return f"{output_function}({function}, {condition_nrql}){label_nrql}"


def _find_query_component(query_config, component_type, component_dict, query_name):
    """Find query component."""
    component_name = query_config[component_type]
    component = component_dict.get(component_name)
    if not component:
        raise InvalidQueryConfigurationException(
            f"Invalid {component_type}, {component_name}, specified for query {query_name}"
        )

    return component


def _parse_output_selection_nrql_component(output_config, filters):
    """Parse an output selection configuration dictionary."""
    if isinstance(output_config, str):
        # Raw NRQL
        return output_config

    if not isinstance(output_config, dict):
        raise InvalidOutputConfigurationException(output_config)

    if "filter" in output_config:
        return _create_filtered_output_selection_nrql(
            "FILTER", output_config["filter"], filters
        )

    if "percentage" in output_config:
        return _create_filtered_output_selection_nrql(
            "PERCENTAGE", output_config["percentage"], filters
        )

    raise InvalidOutputConfigurationException(output_config)


def _parse_query_config(query_name, query_config, filters, output_selections, displays):
    """Parse a query configuration."""
    required_fields = ["filter", "output", "display", "title"]
    for field in required_fields:
        _validate_required_query_field(field, query_config, query_name)

    query_filter = _find_query_component(query_config, "filter", filters, query_name)
    output = _find_query_component(
        query_config, "output", output_selections, query_name
    )
    display = _find_query_component(query_config, "display", displays, query_name)

    return Query(
        name=query_name,
        query_filter=query_filter,
        output=output,
        display=display,
        title=query_config["title"],
        notes=query_config.get("notes"),
    )


def _parse_widget(widget_config, dashboard_name, queries):
    """Parse dashboard widgets from configuration."""
    required_fields = ["query", "row", "column", "width", "height"]
    for field in required_fields:
        _validate_required_widget_field(field, widget_config, dashboard_name)

    query_name = widget_config["query"]
    query = queries.get(query_name)
    if not query:
        raise InvalidWidgetConfigurationException(
            f"Invalid query, {query_name}, specified for widget on dashboard {dashboard_name}"
        )

    widget = Widget(
        title=query.title,
        query=query.to_nrql(),
        notes=query.notes,
        visualization=query.display.visualization,
        row=widget_config["row"],
        column=widget_config["column"],
        width=widget_config["width"],
        height=widget_config["height"],
    )

    return widget


def _validate_required_field(exception, config_type, field_name, config, config_name):
    """Validate required field is present."""
    if field_name not in config:
        raise exception(
            f"Required field {field_name} required for {config_type} {config_name}"
        )


def _validate_required_query_field(field_name, config, query_name):
    """Validate required query field is present."""
    _validate_required_field(
        InvalidQueryConfigurationException, "query", field_name, config, query_name
    )


def _validate_required_widget_field(field_name, config, dashboard_name):
    """Validate required widget field is present."""
    _validate_required_field(
        InvalidWidgetConfigurationException,
        "widget",
        field_name,
        config,
        dashboard_name,
    )
