---
title: Template
weight: 100
---

# `formica template`

Load the CloudFormation template from the `*.template.(yml|yaml|json)` files in the current folder and print it.

## Example

```
 root@07e549506145:/app/docs/examples/s3-bucket# formica template
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

## Usage

```
usage: formica template [-h] [--config-file CONFIG_FILE [CONFIG_FILE ...]]
                        [--vars KEY=Value [KEY=Value ...]] [-y]
                        [--organization-variables]

Print the current template

optional arguments:
  -h, --help            show this help message and exit
  --config-file CONFIG_FILE [CONFIG_FILE ...], -c CONFIG_FILE [CONFIG_FILE ...]
                        Set the config files to use
  --vars KEY=Value [KEY=Value ...]
                        Add one or multiple Jinja2 variables
  -y, --yaml            print output as yaml
  --organization-variables
                        Add AWSAccounts, AWSSubAccounts and AWSRegions as
                        Jinja variables
```