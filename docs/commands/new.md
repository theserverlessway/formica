# `formica new`

Through the new command you can upload your local template to CloudFormation and create a new ChangeSet for a new stack. CloudFormation will create a stack in the **REVIEW_IN_PROGRESS** state until the ChangeSet is deployed. It will fail if the stack already exists. If you decide to not execute the ChangeSet you need to use [`formica remove`](remove.md) to remove the stack and run `formica new` again. After executing it you have to use `formica change`(change.md) to update the Stack. You can see the full template that will be used by running [`formica template`](template.md).

The default name for the created ChangeSet is `STACK_NAME-change-set`, e.g. `formica-stack-change-set`.

After the change was submitted a description of the changes will be printed. For all details on the information in that description check out [`formica describe`](describe.md)

## Options

* `--stack STACK`             The stack you want to create.  [required]
* `--profile PROFILE`         The AWS profile to use.
* `--region REGION`           The AWS region to use.
* `--parameter KEY=Value`     Add a parameter. Repeat for multiple parameters
* `--tag KEY=Value`           Add a stack tag. Repeat for multipe tags
* `--capabilities CAPABILITY_IAM,CAPABILITY_NAMED_IAM`  Set one or multiple stack capabilities