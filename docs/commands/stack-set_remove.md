---
title: StackSet remove
weight: 100
---

# `formica stack-set remove`

The `formica stack-set remove` command allows you to remove a StackSet after you
removed all the instances of that StackSet.

## Options

| Option                                             | Description  |
| -------------------------------------------------- | ------------ |
| --stack-set (-s) STACKSET                          | The StackSet you want to create. |
| --profile PROFILE                                  | The AWS profile to use. |
| --region REGION                                    | The AWS region to use. |

## Usage

```
usage: formica stack-set remove [-h] [--region REGION] [--profile PROFILE]
                                [--stack-set STACK-Set]
                                [--config-file CONFIG_FILE [CONFIG_FILE ...]]

Remove a Stack Set

optional arguments:
  -h, --help            show this help message and exit
  --region REGION       The AWS region to use
  --profile PROFILE     The AWS profile to use
  --stack-set STACK-Set, -s STACK-Set
                        The Stack Set to use
  --config-file CONFIG_FILE [CONFIG_FILE ...], -c CONFIG_FILE [CONFIG_FILE ...]
                        Set the config files to use
```
