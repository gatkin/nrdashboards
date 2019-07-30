# New Relic Dashboard Builder
[![Build Status](https://dev.azure.com/gregscottatkin/New%20Relic%20Dashboard%20Builder/_apis/build/status/gatkin.nrdashboards?branchName=master)](https://dev.azure.com/gregscottatkin/New%20Relic%20Dashboard%20Builder/_build/latest?definitionId=7&branchName=master)
[![Coverage Status](https://coveralls.io/repos/github/gatkin/nrdashboards/badge.svg?branch=HEAD)](https://coveralls.io/github/gatkin/nrdashboards?branch=HEAD)
![GitHub](https://img.shields.io/github/license/gatkin/nrdashboards?color=blue)
[![Code Style](https://img.shields.io/badge/codestyle-black-black)](https://img.shields.io/badge/codestyle-black-black)

New Relic Dashboard Builder is a command-line tool for configuring New Relic dashboards using simple, human-readable YAML files. With New Relic Dashboard Builder, definitions for New Relic dashboards can be kept in version control to support tracking change history for dashboards. Definitions for NRQL queries and widgets can be consolidated into a single canonical location to be shared across multiple dashboards, enabling easier maintenance of a large number of dashboards and widgets.

## Quick Start

With New Relic Dashboard Builder, definitions for dashboards consist of five components:

1. **Conditions** - Specify the conditions used in the `WHERE` clauses of NRQL queries (e.g. `WHERE response.status = 200`)
2. **Output Selections** - Specify the fields and aggregations selected from NRQL queries (e.g. `SELECT COUNT(*)` or `SELECT response.status`)
3. **Displays** - Specify how the data from NRQL queries are displayed by specifying any `SINCE`, `UNTIL`, `WITH TIMEZONE`, `COMPARE WITH`, or `TIMESERIES` clauses
4. **Queries** - Specify full NRQL queries by tying together conditions, output selections, and displays.
5. **Dashboards** - Specify which widgets using which queries go into which dashboards

Below is an example of a dashboard that displays information about transactions from a service

```yaml
conditions:
  web-transactions-condition: transactionType = 'Web'


output-selections:
  total-count-output: COUNT(*)


displays:
  facet-response-status-display:
    nrql: FACET response.status
    visualization: facet_bar_chart


queries:
  web-transactions-by-response-status-query:
    event: Transaction
    condition: web-transactions-condition
    output: total-count-output
    display: facet-response-status-display
    title: Transactions by Response Status


dashboards:
  sample-dashboard:
    title: Sample Dashboard
    widgets:
      - widget:
        query: web-transactions-by-response-status-query
        row: 1
        column: 1
        width: 1
        height: 1
```

To create or update a dashboard in New Relic based on this YAML definition, simply run the New Relic Dashboard Builder tool

```sh
nrdash --api-key <Your-NewRelic-Admin-API-Key> --account-id <Your-NewRelic-Account-Id> dashboards.yml
```