"""Model defintions."""
from typing import Dict

import attr


class NrDashException(Exception):
    """Base class for all application-specific exceptions."""


class InvalidExtendingFilterException(NrDashException):
    """Invalid extending filter exception."""


@attr.s(frozen=True)
class QueryFilter:
    """A query filter component."""

    name: str = attr.ib()
    event: str = attr.ib()
    nrql: str = attr.ib()


@attr.s(frozen=True)
class DashboardConfiguration:
    """Dashboard configuration."""

    filters: Dict[str, QueryFilter] = attr.ib()
