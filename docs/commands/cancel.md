---
title: Cancel
weight: 100
---

# `formica cancel`

Through the cancel command you can cancel a stack update.

After the stack update was started you can cancel it. Formica will wait for the stack to clean up.
If you are creating a stack or all update operations have run and your stack is currently in cleanup mode
the cancel operation will fail.

## Example

```
root@07e549506145:/app/docs/examples/s3-bucket# formica cancel --stack formica-examples-stack
+------------------------------+--------------------------+--------------------------------+--------------------------------+----------------------------------------------------+
|          Timestamp           |          Status          |              Type              |           Logical ID           |                   Status reason                    |
+------------------------------+--------------------------+--------------------------------+--------------------------------+----------------------------------------------------+
2017-02-16 19:14:59 UTC+0000   DELETE_IN_PROGRESS         AWS::CloudFormation::Stack       formica-examples-stack           User Initiated
2017-02-16 19:15:30 UTC+0000   DELETE_IN_PROGRESS         AWS::S3::Bucket                  DeploymentBucket
2017-02-16 19:15:30 UTC+0000   DELETE_IN_PROGRESS         AWS::S3::Bucket                  DeploymentBucket2
2017-02-16 19:15:51 UTC+0000   DELETE_COMPLETE            AWS::S3::Bucket                  DeploymentBucket2
2017-02-16 19:15:51 UTC+0000   DELETE_COMPLETE            AWS::S3::Bucket                  DeploymentBucket
2017-02-16 19:15:52 UTC+0000   DELETE_COMPLETE            AWS::CloudFormation::Stack       formica-examples-stack
```

## Usage

```
usage: formica cancel [-h] [--region REGION] [--profile PROFILE]
                      [--stack STACK]
                      [--config-file CONFIG_FILE [CONFIG_FILE ...]]

Cancel a Stack Update

options:
  -h, --help            show this help message and exit
  --region REGION       The AWS region to use
  --profile PROFILE     The AWS profile to use
  --stack STACK, -s STACK
                        The Stack to use
  --config-file CONFIG_FILE [CONFIG_FILE ...], -c CONFIG_FILE [CONFIG_FILE ...]
                        Set the config files to use
```
