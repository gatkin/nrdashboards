"""Manage New Relic dashboards in source control."""
# import sys

# import yaml

# from nrdash.parsing import parse_file
# from nrdash.nr_api import NewRelicApiClient


# def get_dashboard():
#     """Get dashboard."""
#     client = create_new_relic_client()
#     dashboard = client.get_dashboard(868869)
#     print(dashboard)


# def print_queries():
#     queries = parse_file(sys.argv[1])
#     for query in queries.values():
#         print(query)


# def create_dashboard():
#     client = create_new_relic_client()
#     dashboards = parse_file(sys.argv[1])
#     dashboard = list(dashboards.values())[0]

#     dashboard_id = client.get_dashboard_by_title(dashboard.title)
#     if not dashboard_id:
#         client.create_dashboard(dashboard)
#     else:
#         print(f'Existing dashboard {dashboard_id}')
#         client.update_dashboard(dashboard_id, dashboard)


# def create_new_relic_client():
#     with open("secrets/secrets.yml", "r") as secrets_file:
#         secrets = yaml.safe_load(secrets_file)

#     return NewRelicApiClient(secrets["api-key"], secrets["account-id"])


# if __name__ == "__main__":
#     # get_dashboard()
#     create_dashboard()
