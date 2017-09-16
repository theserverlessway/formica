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

Together with [`formica describe`](describe.md) you can understand exactly what has changed in your template and how that will influence your deployed stack.

## Options

* `--stack STACK`             The stack to diff with.  [required]
* `--profile PROFILE`         The AWS profile to use.
* `--region REGION`           The AWS region to use.