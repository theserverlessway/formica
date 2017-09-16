# `formica deploy`

Through the deploy command you can execute a previously created ChangeSet. This works for both the [`formica new`](new.md) and [`formica change`](change.md) ChangeSets.

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

## Options

* `--stack STACK`             The stack you want to remove.  [required]
* `--profile PROFILE`         The AWS profile to use.
* `--region REGION`           The AWS region to use.