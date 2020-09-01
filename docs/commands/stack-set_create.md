---
title: StackSet Create
weight: 100
---

# `formica stack-set create`

The `formica stack-set create` command allows you to create a new StackSet in your current AWS account.
In a later step you can add/remove instances to the StackSet or update it with a new template.

## Usage

```
usage: formica stack-set create [-h] [--region REGION] [--profile PROFILE]
                                [--stack-set STACK-Set]
                                [--parameters KEY=Value [KEY=Value ...]]
                                [--main-account-parameter]
                                [--tags KEY=Value [KEY=Value ...]]
                                [--capabilities Cap1 Cap2 [Cap1 Cap2 ...]]
                                [--config-file CONFIG_FILE [CONFIG_FILE ...]]
                                [--vars KEY=Value [KEY=Value ...]]
                                [--administration-role-arn ADMINISTRATION_ROLE_ARN]
                                [--administration-role-name ADMINISTRATION_ROLE_NAME]
                                [--execution-role-name EXECUTION_ROLE_NAME]
                                [--organization-variables]
                                [--organization-region-variables]
                                [--organization-account-variables]

Create a Stack Set

optional arguments:
  -h, --help            show this help message and exit
  --region REGION       The AWS region to use
  --profile PROFILE     The AWS profile to use
  --stack-set STACK-Set, -s STACK-Set
                        The Stack Set to use
  --parameters KEY=Value [KEY=Value ...]
                        Add one or multiple stack parameters
  --main-account-parameter
                        Set MainAccount Parameter
  --tags KEY=Value [KEY=Value ...]
                        Add one or multiple stack tags
  --capabilities Cap1 Cap2 [Cap1 Cap2 ...]
                        Set one or multiple stack capabilities
  --config-file CONFIG_FILE [CONFIG_FILE ...], -c CONFIG_FILE [CONFIG_FILE ...]
                        Set the config files to use
  --vars KEY=Value [KEY=Value ...]
                        Add one or multiple Jinja2 variables
  --administration-role-arn ADMINISTRATION_ROLE_ARN
                        The Administration Role to create the StackSet
  --administration-role-name ADMINISTRATION_ROLE_NAME
                        The Administration Role name that will be translated
                        to the ARN
  --execution-role-name EXECUTION_ROLE_NAME
                        The Execution role name to use for the CloudFormation
                        Stack
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
```
