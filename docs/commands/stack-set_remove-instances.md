---
title: StackSet Remove Instances
weight: 100
---

# `formica stack-set remove-instances`

The `formica stack-set remove-instances` command allows you to remove instances from your StackSet for
various accounts and regions. It will remove the stack in every region of every account
you're configuring.

The `--retain` option makes it possible to remove a stack from the StackSet, but keep it in your
AWS account.

## Usage

```
usage: formica stack-set remove-instances [-h] [--region REGION]
                                          [--profile PROFILE]
                                          [--stack-set STACK-Set]
                                          [--accounts ACCOUNTS [ACCOUNTS ...]]
                                          [--regions REGIONS [REGIONS ...]]
                                          [--retain]
                                          [--config-file CONFIG_FILE [CONFIG_FILE ...]]
                                          [--all-accounts] [--all-subaccounts]
                                          [--excluded-accounts EXCLUDED_ACCOUNTS [EXCLUDED_ACCOUNTS ...]]
                                          [--all-regions]
                                          [--excluded-regions EXCLUDED_REGIONS [EXCLUDED_REGIONS ...]]
                                          [--main-account]
                                          [--region-order REGION_ORDER [REGION_ORDER ...]]
                                          [--failure-tolerance-count FAILURE_TOLERANCE_COUNT | --failure-tolerance-percentage FAILURE_TOLERANCE_PERCENTAGE]
                                          [--max-concurrent-count MAX_CONCURRENT_COUNT | --max-concurrent-percentage MAX_CONCURRENT_PERCENTAGE]
                                          [--yes]

Remove Stack Set Instances

optional arguments:
  -h, --help            show this help message and exit
  --region REGION       The AWS region to use
  --profile PROFILE     The AWS profile to use
  --stack-set STACK-Set, -s STACK-Set
                        The Stack Set to use
  --accounts ACCOUNTS [ACCOUNTS ...]
                        The Accounts for this operation
  --regions REGIONS [REGIONS ...]
                        The Regions for this operation
  --retain              Retain stacks
  --config-file CONFIG_FILE [CONFIG_FILE ...], -c CONFIG_FILE [CONFIG_FILE ...]
                        Set the config files to use
  --all-accounts        Use All Accounts of this Org
  --all-subaccounts     Use Only Subaccounts of this Org
  --excluded-accounts EXCLUDED_ACCOUNTS [EXCLUDED_ACCOUNTS ...]
                        All Accounts excluding these
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
  --yes, -y             Answer all input questions with yes
```
