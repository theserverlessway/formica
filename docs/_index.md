---
title: Formica
subtitle: The CloudFormation client you will love
weight: 100
---

[![Build Status](https://travis-ci.org/theserverlessway/formica.svg?branch=master)](https://travis-ci.org/flomotlik/formica)
[![PyPI version](https://badge.fury.io/py/formica-cli.svg)](https://pypi.python.org/pypi/formica-cli)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/theserverlessway/formica/blob/master/LICENSE)
[![Coverage Status](https://coveralls.io/repos/github/flomotlik/formica/badge.svg?branch=master)](https://coveralls.io/github/theserverlessway/formica?branch=master)

Formica makes it easy to create and deploy CloudFormation stacks. It uses CloudFormation syntax with yaml and json support to define your templates. Any existing stack can be used directly, but formica also has built-in modularity so you can reuse and share CloudFormation stack components easily. This allows you to start from an existing stack but split it up into separate files easily.

For dynamic elements in your templates Formica supports [jinja2](http://jinja.pocoo.org/docs/2.9/templates/) as a templating
engine. Jinja2 is widely used, for example in ansible configuration files.

## Installation

Formica can be installed through pip:

```
pip install formica-cli
```

Alternatively you can clone this repository and run

```
python setup.py install
```

After installing Formica take a look at the [quick start guide](#quick-start-guide) or the [examples](examples)

## Why

AWS CloudFormation provides a great service for automatically deploying and updating your infrastructure. But while the service itself is great the tooling to deploy and manage CloudFormation has been lacking. This means that many teams aren't using CloudFormation or automating their infrastructure as much as they should. Formica tries to be a great CloudFormation client by making it easy to build modular templates, make parts of templates reusable and give you great tooling to deploy to and inspect your CloudFormation stacks.

Our goal is that you should never have to log into the AWS Console to look at your CloudFormation stacks, because Formica gives you all the info you need right in your shell.

## AWS Credentials

Formica supports all the standard AWS credential settings, so you can use profiles through the `--profile` option and set the AWS region with `--region`. If you provide no specific profile Formica will use the default profile. You can also use environment variables like **AWS_ACCESS_KEY_ID**. Take a look at the [AWS credentials docs](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html) for more details on how to configure these credentials.

## Quick Start Guide

You define your CloudFormation template through `*.template.(json/yaml/yml)` files. All files named `*.template.(json/yaml/yml)` in the current working directory will be loaded and merged into one large template file before being deployed. This makes it easy to split up your resource files and make each individual file smaller and easier to understand. You can mix `json` and `yaml` files in one directory, which is especially helpful when you start with an existing stack (e.g. one written in JSON) but want to slowly move resources into `yaml` files.

In this example we'll create an S3 Bucket. We use jinja templating to set a variable and use it for the bucket logical name. Put the following into a `bucket.template.yml` file:

```yaml
{% set bucket = "DeploymentBucket" %}
Resources:
  {{ bucket }}:
    Type: "AWS::S3::Bucket"
```

In the same folder run `formica template` which should show you the following template:

```json
{
    "Resources": {
        "DeploymentBucket": {
            "Type": "AWS::S3::Bucket"
        }
    }
}
```

### Create a new Stack

`formica new` will create a ChangeSet for a new Stack in CloudFormation that we can deploy in a next step. It will also describe all the changes that will be done. It also shows CloudFormation `Parameters`, `Tags` and `Capabilities` which can be set through the `--parameters`, `--tags` and `--capabilities` options on the `new` and `change` command.

```
# formica new --stack formica-example-stack
Creating change set for new stack, ...
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
+--------+------------------+------------+-----------------+-------------+---------+
| Action |    LogicalId     | PhysicalId |      Type       | Replacement | Changed |
+========+==================+============+=================+=============+=========+
| Add    | DeploymentBucket |            | AWS::S3::Bucket |             |         |
+--------+------------------+------------+-----------------+-------------+---------+
Change set created, please deploy.
```

You can also use [`formica describe`]({{< relref "/tools/formica/commands/describe.md" >}}) to describe the changes a ChangeSet would perform in a later step. For more detail on the ChangeSet description check out the [describe command documentation]({{< relref "/tools/formica/commands/describe.md" >}}).

All changes, whether you want to create a new stack or update an existing one, are done through [ChangeSets](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets.html). This makes sure you can inspect the specific actions that CloudFormation will take before deploying them. In a CI context you can of course simply run both commands one after the other to get a fully automated deployment.

### Deploy the new Stack

`formica deploy` is used to deploy a previously created ChangeSet. The command will follow the CloudFormation stack events and print them to the command line. If the deployment fails, so will the command.

```
# formica deploy --stack formica-example-stack
+------------------------------+--------------------------+--------------------------------+--------------------------------+----------------------------------------------------+
|          Timestamp           |          Status          |              Type              |           Logical ID           |                   Status reason                    |
+------------------------------+--------------------------+--------------------------------+--------------------------------+----------------------------------------------------+
2017-02-15 10:14:27 UTC+0000   CREATE_IN_PROGRESS         AWS::CloudFormation::Stack       formica-example-stack            User Initiated
2017-02-15 10:14:31 UTC+0000   CREATE_IN_PROGRESS         AWS::S3::Bucket                  DeploymentBucket
2017-02-15 10:14:32 UTC+0000   CREATE_IN_PROGRESS         AWS::S3::Bucket                  DeploymentBucket                 Resource creation Initiated
2017-02-15 10:14:53 UTC+0000   CREATE_COMPLETE            AWS::S3::Bucket                  DeploymentBucket
2017-02-15 10:14:55 UTC+0000   CREATE_COMPLETE            AWS::CloudFormation::Stack       formica-example-stack
```

After the deployment we will now see our new S3 Bucket. As we didn't set a name the name of the bucket is generated by S3:

```
# aws s3 ls
2017-02-15 11:21:18 formica-example-stack-deploymentbucket-57ouvt2o46yh
```

### Creating a Config File

So we don't have to specify the stack name for every command we can also create a config file. The `stack.config.yaml` file we create contains only the stack name but check out the [config file documentation]({{< relref "config-file.md" >}}) for all available options. Add the following content to `stack.config.yaml`. While there is no fixed naming convention *.config.yaml is a best practice:

```yaml
stack: teststack
```

Now you can use the `--config-file` option (or `-c` for short) to set configuration options. CLI Arguments will take precedence over the config file.

### Inspect Stack Resources

We can also check out all the created resources for a stack with the resources command:

```
root@67c57a89511a:/app/docs/examples/s3-bucket# formica resources -c stack.config.yaml
+------------------+------------------------------------------------------+-----------------+-----------------+
|    Logical ID    |                     Physical ID                      |      Type       |     Status      |
+==================+======================================================+=================+=================+
| DeploymentBucket | formica-example-stack-deploymentbucket-57ouvt2o46yh  | AWS::S3::Bucket | CREATE_COMPLETE |
+------------------+------------------------------------------------------+-----------------+-----------------+
```


### Changing the Stack

To add additional resources you can either add it to the file we already created, or put it in a separate file for better modularity. Especially when you have many resources splitting them up into separate files can be very helpful. Check out the [template file documentation]({{< relref "template-files.md" >}}) for more documentation on template files and the [module system]({{< relref "modules.md" >}}) for even more ways to split up your templates and make them reusable.

If we want to add an additional bucket we can add a second file `bucket2.template.json` file with the following content:

```json
{"Resources": {
  "DeploymentBucket2": {
    "Type": "AWS::S3::Bucket"
    }
  }
}
```

Running `formica template` again will now result in both files being picked up and merged:

```json
{
    "Resources": {
        "DeploymentBucket": {
            "Type": "AWS::S3::Bucket"
        },
        "DeploymentBucket2": {
            "Type": "AWS::S3::Bucket"
        }
    }
}
```


`formica diff` allows us to compare the deployed and local template and show an in-depth diff:

```
# formica diff -c stack.config.yaml
+-------------------------------+-------------+-----------------------------+-----------------------+
|             Path              |    From     |             To              |      Change Type      |
+===============================+=============+=============================+=======================+
| Resources > DeploymentBucket2 | Not Present | {'Type': 'AWS::S3::Bucket'} | Dictionary Item Added |
+-------------------------------+-------------+-----------------------------+-----------------------+
```

To deploy this change we can now run the change and deploy command:

```
formica change -c stack.config.yaml
formica deploy -c stack.config.yaml
```

And we can now see both buckets in S3:

```
# aws s3 ls
2017-02-15 11:21:18 formica-example-stack-deploymentbucket-57ouvt2o46yh
2017-02-15 11:21:18 formica-example-stack-deploymentbucket2-1jv31cwqdh5gk
```

### Listing all Stacks

And we can list all the stacks to see the status with `formica stacks`:

```
# formica stacks
Current Stacks:
+-------------------------------+----------------------------------+----------------------------------+-----------------+
|             Name              |            Created At            |            Updated At            |     Status      |
+===============================+==================================+==================================+=================+
| formica-example-stack         | 2017-02-15 10:02:56.809000+00:00 | 2017-02-15 10:57:54.641000+00:00 | UPDATE_COMPLETE |
+-------------------------------+----------------------------------+----------------------------------+-----------------+
```

Last but not least we'll remove the stack with `formica remove -c stack.config.yaml`

```
# formica remove -c stack.config.yaml
Removing Stack and waiting for it to be removed, ...
+------------------------------+--------------------------+--------------------------------+--------------------------------+----------------------------------------------------+
|          Timestamp           |          Status          |              Type              |           Logical ID           |                   Status reason                    |
+------------------------------+--------------------------+--------------------------------+--------------------------------+----------------------------------------------------+
2017-02-15 11:09:07 UTC+0000   DELETE_IN_PROGRESS         AWS::CloudFormation::Stack       formica-example-stack            User Initiated
2017-02-15 11:09:10 UTC+0000   DELETE_IN_PROGRESS         AWS::S3::Bucket                  DeploymentBucket
2017-02-15 11:09:31 UTC+0000   DELETE_COMPLETE            AWS::S3::Bucket                  DeploymentBucket
2017-02-15 11:09:32 UTC+0000   DELETE_COMPLETE            AWS::CloudFormation::Stack       formica-example-stack
```

And now you've created, inspected, updated, deployed and removed a CloudFormation stack with Formica.
