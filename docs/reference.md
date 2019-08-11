# Reference

## Command Line Arguments

To configure New Relic dashboards based on a YAML definition file, the New Relic Dashboard Builder tool must be invoked from the command line with all required arguments.

```sh
Usage: nrdash [OPTIONS] CONFIG_FILE

  Build New Relic dashboards based on YAML configuration.

Options:
  --api-key TEXT        New Relic admin API key  [required]
  --account-id INTEGER  New Relic account id  [required]
  --help                Show this message and exit.
```

## Dashboards

Dashboards definitions are specified under the `dashboards` section. The dashboard title is used to uniquely identify each dashboard in an account. Any existing dashboards on the account with the same title will be overwritten with the definition in the configuration file. A new dashboard will be created if no dashboards exist with the title.

### YAML Snippet

Dashboards can be defined with both inline queries and references to queries defined in the `queries` section

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
      - widget:
        query: sample-query
        row: 3
        column: 1
        width: 1
        height: 1
```

### Arguments

Dashboards are defined with the following set of arguments

| Argument | Description| Required?|
|:----------:|------------|:------------:|
| `title`     | Title of the dashboard. The title is used ot uniquely identify the dashboard and therefore should be unique. | Required |
| `widgets`   | List of widgets that are included in the dashboard. | Required |

Widgets in a dashboard are defined with the following set of arguments

| Argument | Description| Required?|
|:----------:|------------|:------------:|
| `query` | The [query](#queries) that specifies the data displayed by the widget. The query can be either an *inline query* or a *reference* to a query defined in the `queries` section. | Required |
| `row` | The row of the dashboard on which the widget should be displayed. Rows are numbered starting from 1. | Required |
| `column` | The column of dashboard on which the widget should be displayed. Valid column values are 1, 2, or 3. | Required |
| `width` | The width of the widget. Valid width values are 1, 2, or 3. | Required |
| `height` | The height of the widget. | Required |


## Queries

Queries are specified in the `queries` section and define complete NRQL queries that are used to display data in widgets on a dashboard.

### YAML Snippet

Queries can be defined as either *inline queries* or *componentized queries*. Componentized queries allow query components to be shared between multiple queries to avoid duplication in query definitions.

```YAML
queries:
  my-inline-query:
    title: Web Transactions by Response Status
    nrql: SELECT COUNT(*) FROM Transaction WHERE transactionType = 'Web' FACET response.status
    visualization: facet_bar_chart
    notes: Notes about my inline query  # Optional

  my-componentized-query:
    title: My Query
    event: MyEvent
    condition: prod-events  # Optional
    output: total-count
    display: facet-with-timeseries
    notes: Notes about my query  # Optional
```

### Arguments

Inline queries are defined with the following arguments

| Argument | Description| Required?|
|:----------:|------------|:------------:|
| `title` | The title of the query displayed as the title on the widget in the dashboard. | Required |
| `nrql` | The complete NRQL query string. | Required |
| `visualization` | A [widget visualization enum value](#widget-visualization-values). | Required |
| `notes` | Notes for the query displayed as the notes on the widget in the dashboard. | Optional |

Componentized queries are defined with the following arguments

| Argument | Description| Required?|
|:----------:|------------|:------------:|
| `title` | The title of the query displayed as the title on the widget in the dashboard. | Required |
| `event` | The New Relic insights event used in the query. | Required |
| `condition` | The name of the [condition](#conditions) used in the query. | Optional |
| `output` | The name of the [output selection](#output-selections) used in the query. | Required |
| `display` | The name of the [display configuration](#displays) used in the query. | Required |
| `notes` | Notes for the query displayed as the notes on the widget in the dashboard. | Optional |

## Displays

### Widget Visualization Values

The follow widget visualization values are supported as specified in the [New Relic API documentation](https://docs.newrelic.com/docs/insights/insights-api/manage-dashboards/insights-dashboard-api#supported)

* `event_table`
* `line_chart`
* `facet_table`
* `facet_bar_chart`
* `facet_pie_chart`
* `billboard`
* `faceted_area_chart`
* `faceted_line_chart`
* `comparison_line_chart`
* `heatmap`
* `histogram`
* `billboard_comparison`
* `attribute_sheet`
* `funnel`
* `gauge`
* `json`
* `list`

## Output Selections

## Conditions

