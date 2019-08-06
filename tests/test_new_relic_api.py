"""Tests for New Relic API accessor."""
import re

import attr
import responses
import pytest

from nrdash import models, new_relic_api


@attr.s(frozen=True)
class _DashboardResponse:

    title: str = attr.ib()
    dashboard_id: str = attr.ib()


@responses.activate
def test_create_dashboard():
    _set_create_dashboard_response(200)

    _create_dashboard()

    assert len(responses.calls) == 1


@responses.activate
def test_create_dashboard_error():
    _set_create_dashboard_response(500)

    with pytest.raises(models.NewRelicApiException):
        _create_dashboard()


@responses.activate
def test_get_dashboard_id_by_title_error():
    _set_get_dashboards_response(status=500)

    with pytest.raises(models.NewRelicApiException):
        _get_dashboard_id_by_title("My Dashboard")


@responses.activate
def test_get_dashboard_id_by_title_multiple_exact_matches():
    target_title = "My Dashboard"
    response = _set_get_dashboards_response(
        dashboard_responses=[
            _DashboardResponse(title=target_title, dashboard_id=1),
            _DashboardResponse(title=target_title, dashboard_id=7),
        ]
    )

    with pytest.raises(models.NewRelicApiException):
        _get_dashboard_id_by_title(target_title)


@responses.activate
def test_get_dashboard_id_by_title_multiple_matches_with_single_exact_match():
    target_title = "My Dashboard"
    dashboard_id = 1
    response = _set_get_dashboards_response(
        dashboard_responses=[
            _DashboardResponse(title="My Dashboard with Extra Stuff", dashboard_id=7),
            _DashboardResponse(title=target_title, dashboard_id=dashboard_id),
        ]
    )

    actual_dashboard_id = _get_dashboard_id_by_title(target_title)

    assert dashboard_id == actual_dashboard_id


@responses.activate
def test_get_dashboard_id_by_title_no_matches():
    response = _set_get_dashboards_response(
        dashboard_responses=[
            _DashboardResponse(title="Not My Dashboard", dashboard_id=1)
        ]
    )

    actual_dashboard_id = _get_dashboard_id_by_title("My Dashboard")

    assert actual_dashboard_id is None


@responses.activate
def test_get_dashboard_id_by_title_single_exact_match():
    target_title = "My Dashboard"
    dashboard_id = 1
    response = _set_get_dashboards_response(
        dashboard_responses=[
            _DashboardResponse(title=target_title, dashboard_id=dashboard_id)
        ]
    )

    actual_dashboard_id = _get_dashboard_id_by_title(target_title)

    assert dashboard_id == actual_dashboard_id


@responses.activate
def test_update_dashboard():
    _set_update_dashboard_response(200)

    _update_dashboard()

    assert len(responses.calls) == 1


@responses.activate
def test_update_dashboard_error():
    _set_update_dashboard_response(500)

    with pytest.raises(models.NewRelicApiException):
        _update_dashboard()


def _create_client(api_key="API_KEY", account_id=1):
    return new_relic_api.NewRelicApiClient(api_key, account_id)


def _create_dashboard():
    client = _create_client()
    client.create_dashboard(_create_dashboard_data())


def _create_dashboard_data():
    return models.Dashboard(
        name="my-dashboard",
        title="My Dashboard",
        widgets=[
            models.Widget(
                title="My Widget",
                query="SELECT COUNT(*) FROM Transactions",
                visualization=models.WidgetVisualization.BILLBOARD,
                row=1,
                column=1,
                width=1,
                height=1,
                notes="Some Notes",
            )
        ],
    )


def _get_dashboard_id_by_title(title):
    client = _create_client()
    return client.get_dashboard_id_by_title(title)


def _set_create_dashboard_response(status):
    responses.add(responses.POST, new_relic_api.DASHBOARDS_URL, status=status)


def _set_get_dashboards_response(status=200, dashboard_responses=None):
    if dashboard_responses is None:
        dashboards = []
    else:
        dashboards = [
            {"title": response.title, "id": response.dashboard_id}
            for response in dashboard_responses
        ]

    json_response = {"dashboards": dashboards}

    responses.add(
        responses.GET, new_relic_api.DASHBOARDS_URL, status=status, json=json_response
    )


def _set_update_dashboard_response(status):
    responses.add(
        responses.PUT, re.compile(f"{new_relic_api.BASE_URL}.*"), status=status
    )


def _update_dashboard():
    client = _create_client()
    client.update_dashboard(1, _create_dashboard_data())
