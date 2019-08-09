"""Parses input configuration files."""
from enum import Enum
from typing import Dict, Iterable

import attr
import yaml

from .models import (
    ComponentizedQuery,
    Dashboard,
    Widget,
    InvalidExtendingConditionException,
    InvalidOutputConfigurationException,
    InvalidQueryConfigurationException,
    InvalidWidgetConfigurationException,
    Query,
    QueryDisplay,
    QueryCondition,
    QueryOutputSelection,
    WidgetVisualization,
)


class _ExtendingConditionOperator(Enum):
    """Operator used to extend another condition."""

    AND = "AND"
    OR = "OR"


@attr.s(frozen=True)
class _ExtendingQueryCondition:
    """A query condition that extends another query condition."""

    name: str = attr.ib()
    operator: _ExtendingConditionOperator = attr.ib()
    extended_conditions: Iterable[str] = attr.ib()
    nrql_conditions: Iterable[str] = attr.ib()


def parse_conditions(config: Dict) -> Dict[str, QueryCondition]:
    """Parse conditions from configuration."""
    condition_configs = config.get("conditions")
    if not condition_configs:
        return {}

    base_conditions = {}
    extending_conditions = {}
    for name, condition_config in condition_configs.items():
        if isinstance(condition_config, str):
            base_conditions[name] = QueryCondition(name=name, nrql=condition_config)
        else:
            extending_conditions[name] = _parse_extending_condition(
                name, condition_config
            )

    return _resolve_all_extending_conditions(base_conditions, extending_conditions)


def parse_dashboards(config: Dict) -> Dict[str, Dashboard]:
    """Parse dashboards from configuration."""
    dashboard_configs = config.get("dashboards")
    if not dashboard_configs:
        return {}

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
    display_configs = config.get("displays")
    if not display_configs:
        return {}

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


def parse_output_selections(
    config: Dict, conditions: Dict[str, QueryCondition]
) -> Dict[str, QueryOutputSelection]:
    """Parse output selections from configuration."""
    output_configs = config.get("output-selections")
    if not output_configs:
        return {}

    output_selections = {}
    for name, output_config in output_configs.items():
        if isinstance(output_config, str):
            # Raw NRQL
            output_selections[name] = QueryOutputSelection(
                name=name, nrql=f"SELECT {output_config}"
            )
        elif isinstance(output_config, list):
            nrql_components = [
                _parse_output_selection_nrql_component(component_config, conditions)
                for component_config in output_config
            ]

            output_selections[name] = QueryOutputSelection(
                name=name, nrql=f"SELECT {', '.join(nrql_components)}"
            )
        elif isinstance(output_config, dict):
            output_selections[name] = QueryOutputSelection(
                name=name,
                nrql=f"SELECT {_parse_output_selection_nrql_component(output_config, conditions)}",
            )
        else:
            raise InvalidOutputConfigurationException(output_config)

    return output_selections


def parse_queries(config: Dict) -> Dict[str, Query]:
    """Parse queries from configuration."""
    query_configs = config.get("queries")
    if not query_configs:
        return {}

    conditions = parse_conditions(config)
    output_selections = parse_output_selections(config, conditions)
    displays = parse_displays(config)

    queries = {}
    for name, query_config in query_configs.items():
        queries[name] = _parse_query_config(
            name, query_config, conditions, output_selections, displays
        )

    return queries


def _can_condition_be_resolved(base_conditions, extending_condition):
    """Determine whether an extending condition can be resolved."""
    return all(
        condition_name in base_conditions
        for condition_name in extending_condition.extended_conditions
    )


def _create_grouped_output_selection_nrql(output_function, output_config, conditions):
    """Create a grouped output selection."""
    function = output_config["function"]
    label = output_config.get("label")
    if label:
        label_nrql = f" AS `{label}`"
    else:
        label_nrql = ""

    condition = output_config["condition"]
    if condition in conditions:
        condition_nrql = conditions[condition].nrql
    else:
        condition_nrql = condition

    return f"{output_function}({function}, WHERE {condition_nrql}){label_nrql}"


def _find_query_component(query_config, component_type, component_dict, query_name):
    """Find query component."""
    component_name = query_config[component_type]
    component = component_dict.get(component_name)
    if not component:
        raise InvalidQueryConfigurationException(
            f"Invalid {component_type}, {component_name}, specified for query {query_name}"
        )

    return component


def _parse_componentized_query_config(
    query_name, query_config, conditions, output_selections, displays
):
    """Parse a componentized query config."""
    required_fields = ["output", "display", "title", "event"]
    _validate_required_query_fields(required_fields, query_config, query_name)

    if "condition" in query_config:
        condition = _find_query_component(
            query_config, "condition", conditions, query_name
        )
    else:
        condition = None

    output = _find_query_component(
        query_config, "output", output_selections, query_name
    )
    display = _find_query_component(query_config, "display", displays, query_name)

    componentized_query = ComponentizedQuery(
        event=query_config["event"], condition=condition, output=output, display=display
    )

    return Query(
        name=query_name,
        title=query_config["title"],
        nrql=componentized_query.to_nrql(),
        visualization=display.visualization,
        notes=query_config.get("notes"),
    )


def _parse_extending_condition(condition_name, condition_config):
    """Parse an extending condition."""
    if "and" in condition_config:
        operator = _ExtendingConditionOperator.AND
        operand_configs = condition_config["and"]
    elif "or" in condition_config:
        operator = _ExtendingConditionOperator.OR
        operand_configs = condition_config["or"]
    else:
        raise InvalidExtendingConditionException(
            f"Invalid operator for extending condition {condition_name}: {condition_config}"
        )

    extended_conditions = []
    nrql_conditions = []
    for operand_config in operand_configs:
        if isinstance(operand_config, str):
            nrql_conditions.append(operand_config)
        elif isinstance(operand_config, dict) and "condition" in operand_config:
            extended_conditions.append(operand_config["condition"])
        else:
            raise InvalidExtendingConditionException(
                f"Invalid operands for extending condition {condition_name}: {condition_config}"
            )

    if not extended_conditions:
        raise InvalidExtendingConditionException(
            f"Extending condition {condition_name} does not extend any other conditions"
        )

    return _ExtendingQueryCondition(
        name=condition_name,
        operator=operator,
        extended_conditions=extended_conditions,
        nrql_conditions=nrql_conditions,
    )


def _parse_inline_query_config(query_name, query_config):
    """Parse an inline query config."""
    required_fields = ["title", "nrql", "visualization"]
    _validate_required_query_fields(required_fields, query_config, query_name)

    return Query(
        name=query_name,
        title=query_config["title"],
        nrql=query_config["nrql"],
        visualization=WidgetVisualization.from_str(query_config["visualization"]),
        notes=query_config.get("notes"),
    )


def _parse_output_selection_nrql_component(output_config, conditions):
    """Parse an output selection configuration dictionary."""
    if isinstance(output_config, str):
        # Raw NRQL
        return output_config

    if not isinstance(output_config, dict):
        raise InvalidOutputConfigurationException(output_config)

    if "filter" in output_config:
        return _create_grouped_output_selection_nrql(
            "FILTER", output_config["filter"], conditions
        )

    if "percentage" in output_config:
        return _create_grouped_output_selection_nrql(
            "PERCENTAGE", output_config["percentage"], conditions
        )

    raise InvalidOutputConfigurationException(output_config)


def _parse_query_config(
    query_name, query_config, conditions, output_selections, displays
):
    """Parse a query configuration."""
    if "nrql" in query_config:
        return _parse_inline_query_config(query_name, query_config)

    return _parse_componentized_query_config(
        query_name, query_config, conditions, output_selections, displays
    )


def _parse_widget(widget_config, dashboard_name, queries):
    """Parse dashboard widgets from configuration."""
    required_fields = ["query", "row", "column", "width", "height"]
    for field in required_fields:
        _validate_required_widget_field(field, widget_config, dashboard_name)

    query_config = widget_config["query"]

    if isinstance(query_config, str):
        # Refers to a query defined in the "queries" section
        query = queries.get(query_config)
        if not query:
            raise InvalidWidgetConfigurationException(
                f"Invalid query name, {query_config}, specified for widget on dashboard {dashboard_name}"
            )
    else:
        query = _parse_inline_query_config(
            f"{dashboard_name}-inline-query", query_config
        )

    widget = Widget(
        title=query.title,
        query=query.nrql,
        notes=query.notes,
        visualization=query.visualization,
        row=widget_config["row"],
        column=widget_config["column"],
        width=widget_config["width"],
        height=widget_config["height"],
    )

    return widget


def _resolve_all_extending_conditions(base_conditions, extending_conditions):
    """Resolve all conditions that extend other conditions."""
    conditions_to_resolve = len(extending_conditions)
    while conditions_to_resolve > 0:
        unresolved_conditions = [
            extending_condition
            for condition_name, extending_condition in extending_conditions.items()
            if condition_name not in base_conditions
        ]

        resolvable_conditions = [
            extending_condition
            for extending_condition in unresolved_conditions
            if _can_condition_be_resolved(base_conditions, extending_condition)
        ]

        if not resolvable_conditions:
            unresolved_names = ",".join(
                (
                    extending_condition.name
                    for extending_condition in unresolved_conditions
                )
            )
            raise InvalidExtendingConditionException(
                f"Extending conditions do not reference valid conditions and cannot be resolved: {unresolved_names}"
            )

        for extending_condition in resolvable_conditions:
            base_conditions[extending_condition.name] = _resolve_extended_condition(
                base_conditions, extending_condition
            )

        conditions_to_resolve -= len(resolvable_conditions)

    return base_conditions


def _resolve_extended_condition(base_conditions, extending_condition):
    """Resolve extended condition."""
    nrql_conditions = []
    for condition_name in extending_condition.extended_conditions:
        nrql_conditions.append(f"({base_conditions[condition_name].nrql})")

    for condition in extending_condition.nrql_conditions:
        nrql_conditions.append(f"({condition})")

    operator = extending_condition.operator.value
    condition_nrql = f" {operator} ".join(nrql_conditions)

    return QueryCondition(name=extending_condition.name, nrql=condition_nrql)


def _validate_required_field(exception, config_type, field_name, config, config_name):
    """Validate required field is present."""
    if field_name not in config:
        raise exception(
            f"Field {field_name} is required for {config_type} {config_name}"
        )


def _validate_required_query_fields(field_names, config, query_name):
    """Validate all required query fields are present."""
    for field_name in field_names:
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
