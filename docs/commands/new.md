---
title: New
weight: 100
---

# `formica new`

Through the new command you can upload your local template to CloudFormation and create a new ChangeSet for a new stack. CloudFormation will create a stack in the **REVIEW_IN_PROGRESS** state until the ChangeSet is deployed. It will fail if the stack already exists. If you decide to not execute the ChangeSet you need to use [`formica remove`]({{< relref "remove.md" >}}) to remove the stack and run `formica new` again. After executing it you have to use `formica change`({{< relref "change.md" >}}) to update the Stack. You can see the full template that will be used by running [`formica template`]({{< relref "template.md" >}}).

The default name for the created ChangeSet is `STACK_NAME-change-set`, e.g. `formica-stack-change-set`.

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
