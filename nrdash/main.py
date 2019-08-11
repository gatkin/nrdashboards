"""Main entry point for New Relic dashboard builder CLI tool."""
import click

from nrdash import new_relic_api, parsing


@click.command()
@click.argument("config-file", type=str, required=True)
@click.option("--api-key", type=str, required=True, help="New Relic admin API key")
@click.option("--account-id", type=int, required=True, help="New Relic account id")
def build(config_file, api_key, account_id):
    """Build New Relic dashboards based on YAML configuration."""
    dashboards = parsing.parse_file(config_file)
    client = new_relic_api.NewRelicApiClient(api_key, account_id)

    for dashboard in dashboards.values():
        dashboard_id = client.get_dashboard_id_by_title(dashboard.title)
        if dashboard_id:
            print(f"Updating {dashboard.name}")
            client.update_dashboard(dashboard_id, dashboard)
        else:
            print(f"Creating {dashboard.name}")
            client.create_dashboard(dashboard)


def main():
    """Provide main entry point."""
    build()  # pylint: disable=no-value-for-parameter,too-many-function-args


if __name__ == "__main__":
    main()
