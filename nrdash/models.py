"""Model defintions."""
import attr


class NrDashException(Exception):
    """Base class for all application-specific exceptions."""


class InvalidExtendingFilterException(NrDashException):
    """Invalid extending filter exception."""


class InvalidOutputConfigurationException(NrDashException):
    """Invalid output selection configuration exception."""


class InvalidQueryConfigurationException(NrDashException):
    """Invalid query configuration exception."""


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
