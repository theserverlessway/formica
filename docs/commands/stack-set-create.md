---
title: StackSet Create
weight: 100
---

# `formica stack-set create`

The `formica stack-set create` command allows you to create a new StackSet in your current AWS account.
In a later step you can add/remove instances to the StackSet or update it with a new template.

## Options

| Option                                             | Description  |
| -------------------------------------------------- | ------------ |
| --stack-set (-s) STACKSET                          | The StackSet you want to create. |
| --profile PROFILE                                  | The AWS profile to use. |
| --region REGION                                    | The AWS region to use. |
| --parameters KEY1=Value KEY2=Value2                | Add a parameter. Repeat for multiple parameters |
| --tags KEY1=Value KEY2=Value2                      | Add a stack tag. Repeat for multipe tags |
| --vars KEY1=Value KEY2=Value2                      | Add a variable for use in Jinja2 templates. |
| --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM | Set one or multiple stack capabilities |
| --config-file (-c) CONFIG_FILE                     | Set the config files to use |
| --administration-role-arn                          | The Administration Role to create the StackSet |
| --execution-role-name                              | The Execution role name to use for the CloudFormation |
