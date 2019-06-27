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

## Options

| Option                                             | Description  |
| -------------------------------------------------- | ------------ |
| --stack-set (-s) STACKSET                          | The StackSet you want to create. |
| --profile PROFILE                                  | The AWS profile to use. |
| --region REGION                                    | The AWS region to use. |
| --accounts                                         | The Accounts for this operation |
| --regions                                          | The Regions for this operation |
| --retain                                           | Retain stacks |
