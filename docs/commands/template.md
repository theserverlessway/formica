# `formica template`

Load the CloudFormation template from the `*.template.(yml|yaml|json)` files in the current folder and print it.

## Example

```shell
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
