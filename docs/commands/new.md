---
title: New
weight: 100
---

# `formica new`

Through the new command you can upload your local template to CloudFormation and create a new ChangeSet for a new stack. CloudFormation will create a stack in the **REVIEW_IN_PROGRESS** state until the ChangeSet is deployed. It will fail if the stack already exists. If you decide to not execute the ChangeSet you need to use [`formica remove`]({{< relref "remove.md" >}}) to remove the stack and run `formica new` again. After executing it you have to use `formica change`({{< relref "change.md" >}}) to update the Stack. You can see the full template that will be used by running [`formica template`]({{< relref "template.md" >}}).

The default name for the created ChangeSet is `STACK_NAME-change-set`, e.g. `formica-stack-change-set`.

After the change was submitted a description of the changes will be printed. For all details on the information in that description check out [`formica describe`]({{< relref "describe.md" >}})

## Usage

```
usage: formica new [-h] [--region REGION] [--profile PROFILE] [--stack STACK]
                   [--parameters KEY=Value [KEY=Value ...]]
                   [--tags KEY=Value [KEY=Value ...]]
                   [--capabilities Cap1 Cap2 [Cap1 Cap2 ...]]
                   [--role-arn ROLE_ARN] [--role-name ROLE_NAME]
                   [--config-file CONFIG_FILE [CONFIG_FILE ...]]
                   [--vars KEY=Value [KEY=Value ...]] [--s3]
                   [--artifacts ARTIFACTS [ARTIFACTS ...]] [--resource-types]
                   [--organization-variables]
                   [--organization-region-variables]
                   [--organization-account-variables] [--upload-artifacts]

Create a change set for a new stack

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
  --artifacts ARTIFACTS [ARTIFACTS ...]
                        Add one or more artifacts to push to S3 before
                        deployment
  --resource-types      Add Resource Types to the ChangeSet
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
  --upload-artifacts    Upload Artifacts when creating the ChangeSet
```
