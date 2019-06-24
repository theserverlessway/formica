---
title: Configuration File Reference
weight: 300
---

So you don't have to repeat command line options constantly Formica supports config files. Those files allow you to set anything, up to the AWS profile or region to use.
Command line arguments will have precedence over the config files, so you can use a config file, but still change values. Values will be merged, so if you for example specify tags in the config file and on the command line they will be merged or overwritten with the command line taking precedence.

To make it easy to have centralise common options and then have different config files for different environments (e.g. dev/staging/production) you can set multiple config files. They will be loaded in order and will overwrite earlier values. So for example if you set a default Parameter for a stack but then overwrite it in another config file the latter will be used.

Config files can either be json or yaml. The `--config-file` (or `-c` as a shorthand) option can be used to set the config files.

### Example

The following example contains all available options you can set:

```yaml
stack: teststack
parameters:
  BucketName: s3-bucket-name
  SomeParameter: some-value
tags:
  StackTag: formica-test-tag
capabilities:
  - CAPABILITY_IAM
  - CAPABILITY_NAMED_IAM
region: us-east-1
profile: production
vars:
  domain: flomotlik.me
```
