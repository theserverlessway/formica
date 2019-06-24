---
title: Change
weight: 100
---

# `formica change`

Through the change command you can upload your local template to CloudFormation and create a new Changeset for an existing stack. It will fail if the stack doesn't already exist. If you want to create a ChangeSet for a new stack check out `formica new`({{< relref "new.md" >}}). You can see the full template that will be used by running [`formica template`]({{< relref "template.md" >}}).

The default name for the created ChangeSet is `STACK_NAME-change-set`, e.g. `formica-stack-change-set`. If a ChangeSet exists but wasn't deployed it will be removed before creating a new ChangeSet.

After the change was submitted a description of the changes will be printed. For all details on the information in that description check out [`formica describe`]({{< relref "describe.md" >}})

## Options

| Option                                             | Description  |
| -------------------------------------------------- | ------------ |
| --stack (-s) STACK                                 | The stack you want to create. |
| --profile PROFILE                                  | The AWS profile to use. |
| --region REGION                                    | The AWS region to use. |
| --parameters KEY1=Value KEY2=Value2                | Add a parameter. Repeat for multiple parameters |
| --tags KEY1=Value KEY2=Value2                      | Add a stack tag. Repeat for multipe tags |
| --vars KEY1=Value KEY2=Value2                      | Add a variable for use in Jinja2 templates. |
| --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM | Set one or multiple stack capabilities |
| --config-file (-c) CONFIG_FILE                     | Set the config files to use |
| --role-arn ROLE_ARN                                | Set a separate role ARN to pass to the stack |
| --s3                                               | Upload template to S3 before deployment |
