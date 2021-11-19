---
title: Stacks
weight: 100
---

# `formica stacks`

Through the stack command you can get an overview over all the CloudFormation stacks that are in the region you specified.

## Example

```
root@07e549506145:/app# formica stacks
Current Stacks:
+-------------------------------+----------------------------------+----------------------------------+--------------------+
|             Name              |            Created At            |            Updated At            |       Status       |
+===============================+==================================+==================================+====================+
| testuniquestack               | 2017-02-16 17:10:05.424000+00:00 |                                  | REVIEW_IN_PROGRESS |
+-------------------------------+----------------------------------+----------------------------------+--------------------+
| formica-example-stack         | 2017-02-15 11:18:36.430000+00:00 | 2017-02-15 11:40:19.656000+00:00 | UPDATE_COMPLETE    |
+-------------------------------+----------------------------------+----------------------------------+--------------------+
| formica-integration-test-user | 2017-02-10 13:13:24.004000+00:00 | 2017-02-10 15:54:39.394000+00:00 | UPDATE_COMPLETE    |
+-------------------------------+----------------------------------+----------------------------------+--------------------+
| flomotlikme                   | 2017-01-13 16:12:18.300000+00:00 | 2017-02-15 23:03:01.626000+00:00 | UPDATE_COMPLETE    |
+-------------------------------+----------------------------------+----------------------------------+--------------------+
```

## Usage

```
usage: formica stacks [-h] [--region REGION] [--profile PROFILE]
                      [--config-file CONFIG_FILE [CONFIG_FILE ...]]

List all stacks

options:
  -h, --help            show this help message and exit
  --region REGION       The AWS region to use
  --profile PROFILE     The AWS profile to use
  --config-file CONFIG_FILE [CONFIG_FILE ...], -c CONFIG_FILE [CONFIG_FILE ...]
                        Set the config files to use
```
