# Custom Resources

This example implements a CloudFormation custom resource through Lambda.

The code for the custom resource is read from `resource.py` and included directly into the lambda functions CF Code attribute.

The `cfnresponse` module provided by AWS is used to send the result of the lambda call back to CloudFormation.