---
title: StackSet Add Instances
weight: 100
---

# `formica stack-set add-instances`

The `formica stack-set add-instances` command allows you to add instances to your StackSet in
various accounts and regions. It will deploy the StackSet in every region of every account
you're adding.

## Options

| Option                                             | Description  |
| -------------------------------------------------- | ------------ |
| --stack-set (-s) STACKSET                          | The StackSet you want to create. |
| --profile PROFILE                                  | The AWS profile to use. |
| --region REGION                                    | The AWS region to use. |
| --accounts                                         | The Accounts for this operation |
| --regions                                          | The Regions for this operation |
