---
title: Stack Set Diff
weight: 100
---

# `formica stack-set diff`

The `formica stack-set diff` command compares the current local template against the deployed template in the stack-set.
It works the same as [`formica diff`]({{< relref "diff.md" >}}).

```
root@61aaad32daf7:/app/docs/examples/s3-bucket# formica stack-set diff -s teststack
+---------------------------------------------------------+------------------+----------------------------------+-----------------------+
|                          Path                           |       From       |                To                |      Change Type      |
+=========================================================+==================+==================================+=======================+
| Resources > DeploymentBucket > Properties               | Not Present      | {'BucketName': 'another-bucket'} | Dictionary Item Added |
+---------------------------------------------------------+------------------+----------------------------------+-----------------------+
| Resources > DeploymentBucket2 > Properties > BucketName | a-formica-bucket | a-bucket                         | Values Changed        |
+---------------------------------------------------------+------------------+----------------------------------+-----------------------+
```


## Options

| Option                                             | Description  |
| -------------------------------------------------- | ------------ |
| --stack-set (-s) STACK_SET                         | The stack set you want to diff. |
| --profile PROFILE                                  | The AWS profile to use. |
| --region REGION                                    | The AWS region to use. |
| --vars KEY1=Value KEY2=Value2                      | Add a variable for use in Jinja2 templates. |
| --config-file (-c) CONFIG_FILE                     | Set the config files to use |
