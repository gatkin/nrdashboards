"""Parses input configuration files."""
import attr
import yaml

from .models import (
    DashboardConfiguration,
    InvalidExtendingFilterException,
    QueryDisplay,
    QueryFilter,
    QueryOutputSelection,
)


@attr.s(frozen=True)
class _ExtendingQueryFilter:
    """A query filter that extends another query filter."""

    name: str = attr.ib()
    extension_nrql: str = attr.ib()
    extended_filter: str = attr.ib()


def parse_file(config_file_name: str) -> DashboardConfiguration:
    """Parse a configuration file."""
    with open(config_file_name, "r") as config_file:
        config = yaml.safe_load(config_file)

    return DashboardConfiguration(
        filters=_parse_filters(config),
        output_selections=_parse_output_selections(config),
        displays=_parse_displays(config),
    )


def _parse_displays(config):
    """Parse display options from configuration."""
    if "displays" not in config:
        return {}

    display_configs = config["displays"]
    displays = {}
    for name, display_config in display_configs.items():
        displays[name] = QueryDisplay(name=name, nrql=display_config)

    return displays


def _parse_output_selections(config):
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
            raise InvalidExtendingFilterException(output_config)

    return output_selections


def _parse_output_selection_nrql_component(output_config):
    """Parse an output selection configuration dictionary."""
    if isinstance(output_config, str):
        # Raw NRQL
        return output_config

    if not isinstance(output_config, dict):
        raise InvalidExtendingFilterException(output_config)

    if "filter" in output_config:
        return _create_filtered_output_selection_nrql("FILTER", output_config["filter"])

    if "percentage" in output_config:
        return _create_filtered_output_selection_nrql(
            "PERCENTAGE", output_config["percentage"]
        )

    raise InvalidExtendingFilterException(output_config)


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


def _parse_filters(config):
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
