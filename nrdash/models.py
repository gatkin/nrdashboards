"""Model defintions."""
from typing import Dict

import attr


class NrDashException(Exception):
    """Base class for all application-specific exceptions."""


class InvalidExtendingFilterException(NrDashException):
    """Invalid extending filter exception."""


class InvalidOutputConfigurationException(NrDashException):
    """Invalid output selection configuration exception."""


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
class DashboardConfiguration:
    """Dashboard configuration."""

    filters: Dict[str, QueryFilter] = attr.ib()
    output_selections: Dict[str, QueryOutputSelection] = attr.ib()
    displays: Dict[str, QueryDisplay] = attr.ib()
