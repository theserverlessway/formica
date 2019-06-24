---
title: Resources
weight: 100
---

# `formica resources`

Through the resources command you can list all resources for a deployed stack so its easy for you to get the physical id of a resource you deployed.

The command will print the logical id, physical id, type and status.

## Example

```
root@67c57a89511a:/app/docs/examples/s3-bucket# formica resources --stack formica-example-stack
+------------------+------------------------------------------------------+-----------------+-----------------+
|    Logical ID    |                     Physical ID                      |      Type       |     Status      |
+==================+======================================================+=================+=================+
| DeploymentBucket | formica-example-stack-deploymentbucket-1tzvltuaftxso | AWS::S3::Bucket | CREATE_COMPLETE |
+------------------+------------------------------------------------------+-----------------+-----------------+
```

## Options

| Option                                             | Description  |
| -------------------------------------------------- | ------------ |
| --stack (-s) STACK                                 | The stack you want to create. |
| --profile PROFILE                                  | The AWS profile to use. |
| --region REGION                                    | The AWS region to use. |
| --config-file (-c) CONFIG_FILE                     | Set the config files to use |