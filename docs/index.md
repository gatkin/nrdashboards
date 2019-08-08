# Overview

New Relic Dashboard Builder is a tool for declaratively configuring New Relic dashboards using YAML files.

## Design Goals

New Relic Dashboard Builder was designed to help solve the problem of effectively managing a large and growing number of dashboards used to monitor a wide variety of services. It aims to fulfill two design goals that could not be met with using the New Relic UI to create and maintain dashboards:

1. Allow New Relic dashboards to be managed in source control by defining them in simple, human-readable text files.
2. Reduce duplication of query definitions to support easier maintenance of dashboards by
    - Allowing the same query definition to be reused in multiple dashboards.
    - Allowing portions of queries to be combined and reused across multiple queries.


The design of New Relic Dashboard Builder was inspired by the [Jenkins Job Builder](https://docs.openstack.org/infra/jenkins-job-builder/) tool.
