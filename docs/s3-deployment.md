---
title: S3 Deployment
weight: 500
---

Sometimes your template is too large to be deployed directly to the CloudFormation API and has to be pushed to S3 first.

The `--s3` option will create a new bucket, push the template into the bucket and deploy the template to CloudFormation.
After the deployment the template and bucket will be removed.

S3 is only used as transient storage during the deployment and is not considered for longer time storage at the moment.

If you want to limit the buckets formica has access to you can use the following IAM statement to give a user or role
only access to buckets that start with `formica-deploy-`.

```
Statement:
  - Action:
      - 's3:*'
    Effect: Allow
    Resource: arn:aws:s3:::formica-deploy-*
```