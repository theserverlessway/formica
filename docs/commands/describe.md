---
title: Describe
weight: 100
---

# `formica describe`

Through the describe command you can see the changes that would be performed with the current ChangeSet. The output
created by the describe command is also printed when running [`formica new`]({{< relref "new.md" >}}) or [`formica change`]({{< relref "change.md" >}}).

## Example

Before printing the actual changes the output constists of all parameters, tags and capabilities given to either
[`formica new`]({{< relref "new.md" >}}) or [`formica change`]({{< relref "change.md" >}}) when creating the ChangeSet.

After that a table with the following action will be printed:

* **Action**: Action on that resource
* **LogicalId**: Id in the CloudFormationTemplate
* **PhysicalId**: Id of the actual AWS resource (if available), e.g. S3 Bucket name
* **Type**: Type of the Resource
* **Replacement**: True if Resource will be replaced due to action performed against it, empty otherwise
* **Changed**: Any attribute of that resource that will be changed when the ChangeSet gets deployed


```
root@07e549506145:/app/docs/examples/s3-bucket# formica change  --stack formica-example-stack
Removing existing change set
Change set submitted, waiting for CloudFormation to calculate changes ...
Change set created successfully
Deployment metadata:
+---------------+--+
| Parameters    |  |
+---------------+--+
| Tags          |  |
+---------------+--+
| Capabilities  |  |
+---------------+--+

Resource Changes:
+--------+-------------------+-------------------------------------------------------+-----------------+-------------+------------+
| Action |     LogicalId     |                      PhysicalId                       |      Type       | Replacement |  Changed   |
+========+===================+=======================================================+=================+=============+============+
| Remove | DeploymentBucket  | formica-example-stack-deploymentbucket-57ouvt2o46yh   | AWS::S3::Bucket |             |            |
+--------+-------------------+-------------------------------------------------------+-----------------+-------------+------------+
| Modify | DeploymentBucket2 | formica-example-stack-deploymentbucket2-1ov3l9pces9mu | AWS::S3::Bucket | True        | BucketName |
+--------+-------------------+-------------------------------------------------------+-----------------+-------------+------------+
| Add    | DeploymentBucket3 |                                                       | AWS::S3::Bucket |             |            |
+--------+-------------------+-------------------------------------------------------+-----------------+-------------+------------+
```

## Usage

```
usage: formica describe [-h] [--region REGION] [--profile PROFILE]
                        [--stack STACK]
                        [--config-file CONFIG_FILE [CONFIG_FILE ...]]

Describe the latest change-set of the stack

optional arguments:
  -h, --help            show this help message and exit
  --region REGION       The AWS region to use
  --profile PROFILE     The AWS profile to use
  --stack STACK, -s STACK
                        The Stack to use
  --config-file CONFIG_FILE [CONFIG_FILE ...], -c CONFIG_FILE [CONFIG_FILE ...]
                        Set the config files to use
```
