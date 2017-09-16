## Configuration File

So you don't have to repeat command line options constantly Formica supports config files. Those files allow you to set anything, up to the AWS profile or region to use.
Command line arguments will have precedence over the config file, so you can use a config file, but still change values. Values will not be merged, so if you for example specify tags in the config file and on the command line only the command line tags will be used.

Config files can either be json or yaml. The `--config-file` (or `-c` as a shorthand) option can be used to set the config file.

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
```