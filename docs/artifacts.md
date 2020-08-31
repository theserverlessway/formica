---
title: Artifacts
weight: 700
---

Sometimes you might want to upload a Zipfile for a Lambda function or scripts to use with EC2 Auto Scaling groups to S3. To set this up you can use the `--artifacts` argument or config file option.

Artifacts takes a list of file names, reads them and hashes them. These hashes are then used to create a temporary S3 Bucket which will be created at deployment. When creating a changeset, diffing your template or just taking a look at the current template, the same calculations are performed and the Bucket as well as S3 Object name will be set in Jinja variables so you can access them.

The bucket will always start with `formica-deploy-` followed by the bucket hash so you can set up IAM Roles for deployment to have access to resources starting with this prefix.

Because the files are hashed when the files don't change neither do your templates and CloudFormation will not redeploy any resources.

A simple example would be the following artifact for a Lambda function. The example can also be seen in the [S3-Lambda Example](examples/s3-lambda) At first we're zipping `code.py` into `build/code.py.zip`.:

```
mkdir -p build
zip build/code.py.zip code.py
```

Now we add the artifacts to the configuration file:

```
stack: s3-lambda
capabilities:
  - CAPABILITY_IAM
artifacts:
  - build/code.py.zip
```

In our lambda function config we can then use the artifact file name to get to the bucket and key:

```
TestFunctionS3:
    Type: AWS::Lambda::Function
    Properties:
      Code:
        S3Bucket: {{artifacts['build/code.py.zip'].bucket}}
        S3Key: {{artifacts['build/code.py.zip'].key}}
      Handler: code.handler
      Role:
        Fn::GetAtt:
          - LambdaExecutionRole
          - Arn
      Runtime: python3.8
```

The full path is used for referencing the specific file. Based on the file content we'll create hashes and all the hashes of the files will be used to create a hash used  for the bucket name. In addition the AccountID and Region will be used for the bucket hash to make sure its unique and scoped to the account and region.

After deployment the bucket and all objects in it will be removed.