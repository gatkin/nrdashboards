# Overview

New Relic Dashboard Builder is a command line tool for declaratively configuring New Relic dashboards using YAML files.

## Design Goals

New Relic Dashboard Builder was designed to help solve the problem of effectively managing a large and growing number of dashboards used to monitor a wide variety of services. It aims to fulfill two design goals that could not be met with using the New Relic UI to create and maintain dashboards:

1. Allow New Relic dashboards to be managed in source control by defining them in simple, human-readable text files.
2. Reduce duplication of query definitions to support easier maintenance of dashboards by
    - Allowing the same query definition to be reused in multiple dashboards.
    - Allowing portions of queries to be combined and reused across multiple queries.


The design of New Relic Dashboard Builder was inspired by the [Jenkins Job Builder](https://docs.openstack.org/infra/jenkins-job-builder/) tool.

## Installation

The New Relic Dashboard Builder command line tool that can be installed from [PyPI](https://pypi.org/project/nrdash/) using pip

```sh
pip install nrdash
```

## Usage

To use New Relic Dashboard Builder, you must first acquire an [**admin** New Relic API key](https://docs.newrelic.com/docs/insights/insights-api/manage-dashboards/insights-dashboard-api#requirements). Once you have an admin API key, you can provide the admin API key and your dashboard configuration YAML file to the  New Relic Dashboard Builder command line tool.

```sh
nrdash --api-key <YOUR_ADMIN_API_KEY> --account-id <YOUR_ACCOUNT_ID> <DASHBOARD_DEFINITION_YAML_FILE>
```
