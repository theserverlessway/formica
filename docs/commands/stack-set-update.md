---
title: StackSet Update
weight: 100
---

# `formica stack-set update`

The `formica stack-set update` command allows you to update a StackSet in your current AWS account
with the template in your current folder. You can use the same parameters as in create, but
can also limit which accounts/regions defined in your StackSet should be updated. This is helpful
for deploying to selected accounts/regions first to see if everything works out fine.

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
| --execution-role-name                              | The Execution role name to use for the CloudFormation
| --accounts                                         | The Accounts for this operation |
| --regions                                          | The Regions for this operation |
