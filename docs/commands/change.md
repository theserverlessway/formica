---
title: Change
weight: 100
---

# `formica change`

Through the change command you can upload your local template to CloudFormation and create a new Changeset for an existing stack. It will fail if the stack doesn't already exist. If you want to create a ChangeSet for a new stack check out `formica new`({{< relref "new.md" >}}). You can see the full template that will be used by running [`formica template`]({{< relref "template.md" >}}).

The default name for the created ChangeSet is `STACK_NAME-change-set`, e.g. `formica-stack-change-set`. If a ChangeSet exists but wasn't deployed it will be removed before creating a new ChangeSet.

After the change was submitted a description of the changes will be printed. For all details on the information in that description check out [`formica describe`]({{< relref "describe.md" >}})

## Usage

```
usage: formica change [-h] [--region REGION] [--profile PROFILE]
                      [--stack STACK] [--parameters KEY=Value [KEY=Value ...]]
                      [--tags KEY=Value [KEY=Value ...]]
                      [--capabilities Cap1 Cap2 [Cap1 Cap2 ...]]
                      [--role-arn ROLE_ARN] [--role-name ROLE_NAME]
                      [--config-file CONFIG_FILE [CONFIG_FILE ...]]
                      [--vars KEY=Value [KEY=Value ...]] [--s3]
                      [--resource-types] [--organization-variables]

Create a change set for an existing stack

optional arguments:
  -h, --help            show this help message and exit
  --region REGION       The AWS region to use
  --profile PROFILE     The AWS profile to use
  --stack STACK, -s STACK
                        The Stack to use
  --parameters KEY=Value [KEY=Value ...]
                        Add one or multiple stack parameters
  --tags KEY=Value [KEY=Value ...]
                        Add one or multiple stack tags
  --capabilities Cap1 Cap2 [Cap1 Cap2 ...]
                        Set one or multiple stack capabilities
  --role-arn ROLE_ARN   Set a separate role ARN to pass to the stack
  --role-name ROLE_NAME
                        Set a role name that will be translated to the ARN
  --config-file CONFIG_FILE [CONFIG_FILE ...], -c CONFIG_FILE [CONFIG_FILE ...]
                        Set the config files to use
  --vars KEY=Value [KEY=Value ...]
                        Add one or multiple Jinja2 variables
  --s3                  Upload template to S3 before deployment
  --resource-types      Add Resource Types to the ChangeSet
  --organization-variables
                        Add AWSAccounts, AWSSubAccounts and AWSRegions as
                        Jinja variables
```
