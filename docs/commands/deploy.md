---
title: Deploy
weight: 100
---

# `formica deploy`

Through the deploy command you can execute a previously created ChangeSet. This works for both the [`formica new`]({{< relref "new.md" >}}) and [`formica change`]({{< relref "change.md" >}}) ChangeSets.

 After starting the update to the stack it will follow the stack events until the deployment is finshed. In case the deployment failed it will exit with a non-zero exit status.

## Example

```
root@07e549506145:/app/docs/examples/s3-bucket# formica deploy --stack formica-examples-stack
+------------------------------+--------------------------+--------------------------------+--------------------------------+----------------------------------------------------+
|          Timestamp           |          Status          |              Type              |           Logical ID           |                   Status reason                    |
+------------------------------+--------------------------+--------------------------------+--------------------------------+----------------------------------------------------+
2017-02-16 19:12:51 UTC+0000   CREATE_IN_PROGRESS         AWS::CloudFormation::Stack       formica-examples-stack           User Initiated
2017-02-16 19:13:01 UTC+0000   CREATE_IN_PROGRESS         AWS::S3::Bucket                  DeploymentBucket
2017-02-16 19:13:01 UTC+0000   CREATE_IN_PROGRESS         AWS::S3::Bucket                  DeploymentBucket2
2017-02-16 19:13:02 UTC+0000   CREATE_IN_PROGRESS         AWS::S3::Bucket                  DeploymentBucket                 Resource creation Initiated
2017-02-16 19:13:02 UTC+0000   CREATE_IN_PROGRESS         AWS::S3::Bucket                  DeploymentBucket2                Resource creation Initiated
2017-02-16 19:13:23 UTC+0000   CREATE_COMPLETE            AWS::S3::Bucket                  DeploymentBucket
2017-02-16 19:13:23 UTC+0000   CREATE_COMPLETE            AWS::S3::Bucket                  DeploymentBucket2
2017-02-16 19:13:25 UTC+0000   CREATE_COMPLETE            AWS::CloudFormation::Stack       formica-examples-stack
```

## Usage

```
usage: formica deploy [-h] [--region REGION] [--profile PROFILE]
                      [--artifacts ARTIFACTS [ARTIFACTS ...]] [--stack STACK]
                      [--config-file CONFIG_FILE [CONFIG_FILE ...]]
                      [--timeout TIMEOUT] [--disable-rollback]

Deploy the latest change set for a stack

options:
  -h, --help            show this help message and exit
  --region REGION       The AWS region to use
  --profile PROFILE     The AWS profile to use
  --artifacts ARTIFACTS [ARTIFACTS ...]
                        Add one or more artifacts to push to S3 before
                        deployment
  --stack STACK, -s STACK
                        The Stack to use
  --config-file CONFIG_FILE [CONFIG_FILE ...], -c CONFIG_FILE [CONFIG_FILE ...]
                        Set the config files to use
  --timeout TIMEOUT     Set the Timeout in minutes before the Update is
                        canceled
  --disable-rollback    Do not roll back in case of a failed deployment
```
