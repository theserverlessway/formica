---
title: Diff
weight: 100
---

# `formica diff`

Through the diff command you can see exactly what changed in your template compared to what is already deployed in your stack. It uses [DeepDiff](https://github.com/seperman/deepdiff) to compare the two templates and show you detailed results.

Following is an example where we have two S3 Buckets and want to add a specific BucketName for one and change the BucketName of the second.

```
root@61aaad32daf7:/app/docs/examples/s3-bucket# formica diff --stack teststack
+---------------------------------------------------------+------------------+----------------------------------+-----------------------+
|                          Path                           |       From       |                To                |      Change Type      |
+=========================================================+==================+==================================+=======================+
| Resources > DeploymentBucket > Properties               | Not Present      | {'BucketName': 'another-bucket'} | Dictionary Item Added |
+---------------------------------------------------------+------------------+----------------------------------+-----------------------+
| Resources > DeploymentBucket2 > Properties > BucketName | a-formica-bucket | a-bucket                         | Values Changed        |
+---------------------------------------------------------+------------------+----------------------------------+-----------------------+
```

As you can see it will show the path of the property that was changed, what it was before and after and what kind of change it was.

Together with [`formica describe`]({{< relref "describe.md" >}}) you can understand exactly what has changed in your template and how that will influence your deployed stack.

## Usage

```
usage: formica diff [-h] [--region REGION] [--profile PROFILE] [--stack STACK]
                    [--config-file CONFIG_FILE [CONFIG_FILE ...]]
                    [--vars KEY=Value [KEY=Value ...]]
                    [--parameters KEY=Value [KEY=Value ...]]
                    [--tags KEY=Value [KEY=Value ...]]
                    [--organization-variables]

Print a diff between local and deployed stack

optional arguments:
  -h, --help            show this help message and exit
  --region REGION       The AWS region to use
  --profile PROFILE     The AWS profile to use
  --stack STACK, -s STACK
                        The Stack to use
  --config-file CONFIG_FILE [CONFIG_FILE ...], -c CONFIG_FILE [CONFIG_FILE ...]
                        Set the config files to use
  --vars KEY=Value [KEY=Value ...]
                        Add one or multiple Jinja2 variables
  --parameters KEY=Value [KEY=Value ...]
                        Add one or multiple stack parameters
  --tags KEY=Value [KEY=Value ...]
                        Add one or multiple stack tags
  --organization-variables
                        Add AWSAccounts, AWSSubAccounts, AWSMainAccount and
                        AWSRegions as Jinja variables with an Email, Id and
                        Name field for each account
```
