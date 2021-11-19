---
title: Change
weight: 100
---

# `formica change`

Through the change command you can upload your local template to CloudFormation and create a new Changeset for an existing stack. It will fail if the stack doesn't already exist. If you want to create the missing stack use the `--create-missing` option. In general try to use `formica new` when creating a new Stack so you don't accidentally creates stacks when running change. For automation it is sometimes useful though to create them if they aren't there yet. 

If you want to create a ChangeSet for a new stack check out `formica new`({{< relref "new.md" >}}). You can see the full template that will be used by running [`formica template`]({{< relref "template.md" >}}).

The default name for the created ChangeSet is `STACK_NAME-change-set`, e.g. `formica-stack-change-set`. If a ChangeSet exists but wasn't deployed it will be removed before creating a new ChangeSet.

After the change was submitted a description of the changes will be printed. For all details on the information in that description check out [`formica describe`]({{< relref "describe.md" >}})

For nested Stacks you have the option to create nested ChangeSets via the `--nested-change-sets` option and `nested_change_sets` config file option. Those will give details about the changes proposed for each nested Stack as well as for the main Stack.

## Usage

```
usage: formica change [-h] [--region REGION] [--profile PROFILE]
                      [--stack STACK] [--parameters KEY=Value [KEY=Value ...]]
                      [--tags KEY=Value [KEY=Value ...]]
                      [--capabilities Cap1 Cap2 [Cap1 Cap2 ...]]
                      [--role-arn ROLE_ARN] [--role-name ROLE_NAME]
                      [--config-file CONFIG_FILE [CONFIG_FILE ...]]
                      [--vars KEY=Value [KEY=Value ...]] [--s3]
                      [--artifacts ARTIFACTS [ARTIFACTS ...]]
                      [--resource-types] [--create-missing]
                      [--organization-variables]
                      [--organization-region-variables]
                      [--organization-account-variables]
                      [--use-previous-template] [--use-previous-parameters]
                      [--upload-artifacts] [--nested-change-sets]

Create a change set for an existing stack

options:
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
  --artifacts ARTIFACTS [ARTIFACTS ...]
                        Add one or more artifacts to push to S3 before
                        deployment
  --resource-types      Add Resource Types to the ChangeSet
  --create-missing      Create the Stack in case it's missing
  --organization-variables
                        Add AWSAccounts, AWSSubAccounts, AWSMainAccount and
                        AWSRegions as Jinja variables with an Email, Id and
                        Name field for each account
  --organization-region-variables
                        Add AWSRegions as Jinja variables
  --organization-account-variables
                        Add AWSAccounts, AWSSubAccounts, and AWSMainAccount as
                        Jinja variables with an Email, Id, and Name field for
                        each account
  --use-previous-template
                        Use the previously deployed template
  --use-previous-parameters
                        Reuse Stack Parameters not specifically set
  --upload-artifacts    Upload Artifacts when creating the ChangeSet
  --nested-change-sets  Create a ChangeSet for nested Stacks
```
