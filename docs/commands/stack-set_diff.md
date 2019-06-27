---
title: StackSet Diff
weight: 100
---

# `formica stack-set diff`

The `formica stack-set diff` command compares the current local template against the deployed template in the stack-set.
It works the same as [`formica diff`]({{< relref "diff.md" >}}).

```
root@61aaad32daf7:/app/docs/examples/s3-bucket# formica stack-set diff -s teststack
+---------------------------------------------------------+------------------+----------------------------------+-----------------------+
|                          Path                           |       From       |                To                |      Change Type      |
+=========================================================+==================+==================================+=======================+
| Resources > DeploymentBucket > Properties               | Not Present      | {'BucketName': 'another-bucket'} | Dictionary Item Added |
+---------------------------------------------------------+------------------+----------------------------------+-----------------------+
| Resources > DeploymentBucket2 > Properties > BucketName | a-formica-bucket | a-bucket                         | Values Changed        |
+---------------------------------------------------------+------------------+----------------------------------+-----------------------+
```

## Usage

```
usage: formica stack-set diff [-h] [--region REGION] [--profile PROFILE]
                              [--stack-set STACK-Set]
                              [--config-file CONFIG_FILE [CONFIG_FILE ...]]
                              [--parameters KEY=Value [KEY=Value ...]]
                              [--tags KEY=Value [KEY=Value ...]]
                              [--vars KEY=Value [KEY=Value ...]]
                              [--organization-variables]
                              [--main-account-parameter]

Diff the StackSet template to the local template

optional arguments:
  -h, --help            show this help message and exit
  --region REGION       The AWS region to use
  --profile PROFILE     The AWS profile to use
  --stack-set STACK-Set, -s STACK-Set
                        The Stack Set to use
  --config-file CONFIG_FILE [CONFIG_FILE ...], -c CONFIG_FILE [CONFIG_FILE ...]
                        Set the config files to use
  --parameters KEY=Value [KEY=Value ...]
                        Add one or multiple stack parameters
  --tags KEY=Value [KEY=Value ...]
                        Add one or multiple stack tags
  --vars KEY=Value [KEY=Value ...]
                        Add one or multiple Jinja2 variables
  --organization-variables
                        Add AWSAccounts, AWSSubAccounts and AWSRegions as
                        Jinja variables
  --main-account-parameter
                        Set MainAccount Parameter
```
