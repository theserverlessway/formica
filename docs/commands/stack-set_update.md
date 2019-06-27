---
title: StackSet Update
weight: 100
---

# `formica stack-set update`

The `formica stack-set update` command allows you to update a StackSet in your current AWS account
with the template in your current folder. You can use the same parameters as in create, but
can also limit which accounts/regions defined in your StackSet should be updated. This is helpful
for deploying to selected accounts/regions first to see if everything works out fine.

## Usage

```
usage: formica stack-set update [-h] [--region REGION] [--profile PROFILE]
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
                                [--accounts ACCOUNTS [ACCOUNTS ...]]
                                [--regions REGIONS [REGIONS ...]]
                                [--all-accounts] [--all-subaccounts]
                                [--all-regions]
                                [--excluded-regions EXCLUDED_REGIONS [EXCLUDED_REGIONS ...]]
                                [--main-account]
                                [--region-order REGION_ORDER [REGION_ORDER ...]]
                                [--failure-tolerance-count FAILURE_TOLERANCE_COUNT | --failure-tolerance-percentage FAILURE_TOLERANCE_PERCENTAGE]
                                [--max-concurrent-count MAX_CONCURRENT_COUNT | --max-concurrent-percentage MAX_CONCURRENT_PERCENTAGE]
                                [--organization-variables] [--yes]

Update a Stack Set

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
  --accounts ACCOUNTS [ACCOUNTS ...]
                        The Accounts for this operation
  --regions REGIONS [REGIONS ...]
                        The Regions for this operation
  --all-accounts        Use All Accounts of this Org
  --all-subaccounts     Use Only Subaccounts of this Org
  --all-regions         Use all Regions
  --excluded-regions EXCLUDED_REGIONS [EXCLUDED_REGIONS ...]
                        Excluded Regions from deployment
  --main-account        Deploy to Main Account only
  --region-order REGION_ORDER [REGION_ORDER ...]
                        Order in which to deploy to regions
  --failure-tolerance-count FAILURE_TOLERANCE_COUNT
                        Number of Stacks to fail before failing operation
  --failure-tolerance-percentage FAILURE_TOLERANCE_PERCENTAGE
                        Percentage of Stacks to fail before failing operation
  --max-concurrent-count MAX_CONCURRENT_COUNT
                        Max Number of concurrent accounts to deploy to
  --max-concurrent-percentage MAX_CONCURRENT_PERCENTAGE
                        Max Percentage of concurrent accounts to deploy to
  --organization-variables
                        Add AWSAccounts, AWSSubAccounts and AWSRegions as
                        Jinja variables
  --yes, -y             Answer all input questions with yes
```
