---
title: Remove
weight: 100
---

# `formica remove`

Through the remove command you can remove an existing stack.

After starting to remove the stack it will follow the stack events until the removal is finshed. In case the removal failed it will exit with a non-zero exit status.

## Example

```
root@07e549506145:/app/docs/examples/s3-bucket# formica remove --stack formica-examples-stack
Removing Stack and waiting for it to be removed, ...
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
usage: formica remove [-h] [--region REGION] [--profile PROFILE]
                      [--stack STACK] [--role-arn ROLE_ARN]
                      [--role-name ROLE_NAME]
                      [--config-file CONFIG_FILE [CONFIG_FILE ...]]

Remove the configured stack

optional arguments:
  -h, --help            show this help message and exit
  --region REGION       The AWS region to use
  --profile PROFILE     The AWS profile to use
  --stack STACK, -s STACK
                        The Stack to use
  --role-arn ROLE_ARN   Set a separate role ARN to pass to the stack
  --role-name ROLE_NAME
                        Set a role name that will be translated to the ARN
  --config-file CONFIG_FILE [CONFIG_FILE ...], -c CONFIG_FILE [CONFIG_FILE ...]
                        Set the config files to use
```
