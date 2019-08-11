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
| `query` | The query that specifies the data displayed by the widget. The query can be either an *inline query* or a *reference* to a query defined in the `queries` section. | Required |
| `row` | The row of the dashboard on which the widget should be displayed. Rows are numbered starting from 1. | Required |
| `column` | The column of dashboard on which the widget should be displayed. Valid column values are 1, 2, or 3. | Required |
| `width` | The width of the widget. Valid width values are 1, 2, or 3. | Required |
| `height` | The height of the widget. | Required |


## Queries

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

