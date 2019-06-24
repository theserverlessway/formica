---
title: Wait
weight: 100
---

# `formica wait`

The Wait command allows you to wait for any stack to finish an update or removal. It will start following
the stack from the last event and list all events until the stack has finished the current operation.

## Example

```
root@07e549506145:/app/docs/examples/s3-bucket# formica wait --stack formica-examples-stack
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

## Options

| Option                                             | Description  |
| -------------------------------------------------- | ------------ |
| --stack (-s) STACK                                 | The stack you want to create. |
| --profile PROFILE                                  | The AWS profile to use. |
| --region REGION                                    | The AWS region to use. |
| --config-file (-c) CONFIG_FILE                     | Set the config files to use |
