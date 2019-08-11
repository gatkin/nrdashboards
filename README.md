# New Relic Dashboard Builder
[![Build Status](https://dev.azure.com/gregscottatkin/New%20Relic%20Dashboard%20Builder/_apis/build/status/gatkin.nrdashboards?branchName=master)](https://dev.azure.com/gregscottatkin/New%20Relic%20Dashboard%20Builder/_build/latest?definitionId=7&branchName=master)
[![Docs](https://img.shields.io/badge/docs-yes-blue)](https://gatkin.github.io/nrdashboards/)
[![PyPI Package](https://img.shields.io/pypi/v/nrdash)](https://pypi.org/project/nrdash/)
[![Coverage Status](https://coveralls.io/repos/github/gatkin/nrdashboards/badge.svg?branch=HEAD)](https://coveralls.io/github/gatkin/nrdashboards?branch=HEAD)
[![License](https://img.shields.io/github/license/gatkin/nrdashboards?color=blue)](https://github.com/gatkin/nrdashboards/blob/master/LICENSE)
[![Code Style](https://img.shields.io/badge/codestyle-black-black)](https://black.readthedocs.io/en/stable/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nrdash)](https://pypi.org/project/nrdash/)

New Relic Dashboard Builder is a command-line tool for configuring New Relic dashboards using simple, human-readable YAML files. With New Relic Dashboard Builder, definitions for New Relic dashboards can be kept in version control to support tracking change history for dashboards. Definitions for NRQL queries and widgets can be consolidated into a single canonical location to be shared across multiple dashboards, enabling easier maintenance of a large number of dashboards and widgets.

## Usage

Install with pip, note that New Relic Dashboard Builder only works with Python 3.6 or higher

```sh
pip install nrdash
```

Create your dashboard definitions in a YAML file

```yaml
dashboards:
  sample-dashboard:
    title: Sample Dashboard
    widgets:
      - widget:
        query:
          title: Transactions by Response Status
          nrql: SELECT COUNT(*) FROM Transaction WHERE transactionType = 'Web' FACET response.status
          visualization: facet_bar_chart
        row: 1
        column: 1
        width: 3
        height: 2
```

Run the New Relic Dashboard Builder tool to create or update your New Relic dashboards based on the YAML definition file.

```sh
nrdash --api-key <YOUR_ADMIN_API_KEY> --account-id <YOUR_ACCOUNT_ID> <DASHBOARD_DEFINITION_YAML_FILE>
```

## Documentation

See the [documentation site](https://gatkin.github.io/nrdashboards/) for complete documentation.