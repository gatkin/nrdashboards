"""Parses input configuration files."""
import attr
import yaml

from .models import DashboardConfiguration, InvalidExtendingFilterException, QueryFilter


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

    return DashboardConfiguration(filters=_parse_filters(config))


def _parse_filters(config):
    """Parse filters from configuration."""
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
