"""New Relic API client."""
from typing import Dict, Optional

import requests

from .models import Dashboard, Widget, NewRelicApiException


BASE_URL = "https://api.newrelic.com/v2/"
DASHBOARDS_URL = BASE_URL + "dashboards.json"


class NewRelicApiClient:
    """New Relic API client."""

    def __init__(self, api_key: str, account_id: int) -> None:
        """Initialize API accessor with API key and account id."""
        self._api_key = api_key
        self._account_id = account_id

    def create_dashboard(self, dashboard: Dashboard) -> None:
        """Create a new dashboard."""
        self._send_dashboard_data(requests.post, DASHBOARDS_URL, dashboard)

    def get_dashboard_id_by_title(self, dashboard_title: str) -> Optional[int]:
        """Get dashboard id by title, returns None if there is no dashboard with the provided name."""
        params = {"filter[title]": dashboard_title}
        response = requests.get(
            DASHBOARDS_URL, headers=self._auth_headers(), params=params
        )
        if response.status_code != 200:
            raise NewRelicApiException(
                f"Failed getting dashboard {dashboard_title} with status = {response.status_code}, response = {response.content}"
            )

        dashboards = response.json()

        # The API call returns all dashboards whose titles contain the string provided to the filter.
        # Find the single dashboard with the same name. This assumes that dashboard names are unique when
        # using this tool.
        matching_dashboards = [
            dashboard
            for dashboard in dashboards["dashboards"]
            if dashboard["title"] == dashboard_title
        ]

        if not matching_dashboards:
            return None

        if len(matching_dashboards) > 1:
            raise NewRelicApiException(
                f"Multiple dashboards found with title '{dashboard_title}'"
            )

        return matching_dashboards[0]["id"]

    def update_dashboard(self, dashboard_id: int, dashboard: Dashboard) -> None:
        """Update an existing dashboard with the given id."""
        url = f"{BASE_URL}dashboards/{dashboard_id}.json"
        self._send_dashboard_data(requests.put, url, dashboard)

    def _auth_headers(self):
        """Get headers for making authenticated requests."""
        return {"X-Api-Key": self._api_key}

    def _dashboard_to_dict(self, dashboard: Dashboard) -> Dict:
        """Convert a dashboard into a dictionary that can be posted to the New Relic API."""
        widgets = [self._widget_to_dict(widget) for widget in dashboard.widgets]
        return {
            "dashboard": {
                "metadata": {"version": 1},
                "title": dashboard.title,
                "icon": "usd",
                "visibility": "all",
                "editable": "editable_by_all",
                "filter": {},
                "widgets": widgets,
            }
        }

    def _send_dashboard_data(self, http_call, url, dashboard):
        """Send dashboard data to New Relic API."""
        dashboard_dict = self._dashboard_to_dict(dashboard)
        response = http_call(url, headers=self._auth_headers(), json=dashboard_dict)

        if response.status_code not in (200, 201):
            raise NewRelicApiException(
                f"Failed creating dashboard {dashboard.name} with status = {response.status_code}, response = {response.content}"
            )

    def _widget_to_dict(self, widget: Widget) -> Dict:
        """Convert a widget into a dictionary that can be posted to the New Relic API."""
        return {
            "account_id": self._account_id,
            "visualization": widget.visualization.value,
            "data": [{"nrql": widget.query}],
            "presentation": {"title": widget.title, "notes": widget.notes},
            "layout": {
                "width": widget.width,
                "height": widget.height,
                "row": widget.row,
                "column": widget.column,
            },
        }
