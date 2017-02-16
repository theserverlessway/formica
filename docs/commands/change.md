# `formica change`

Through the change command you can upload your local template to CloudFormation and create a new Changeset for an existing stack. It will fail if the stack doesn't already exist. If you want to create a ChangeSet for a new stack check out `formica new`(new.md). You can see the full template that will be used by running [`formica template`](template.md).

The default name for the created ChangeSet is `STACK_NAME-change-set`, e.g. `formica-stack-change-set`. If a ChangeSet exists but wasn't deployed it will be removed before creating a new ChangeSet.

After the change was submitted a description of the changes will be printed. For all details on the information in that description check out [`formica describe`](describe.md)

## Options

* `--stack STACK`             The stack to submit your changes to.  [required]
* `--profile PROFILE`         The AWS profile to use.
* `--region REGION`           The AWS region to use.
* `--parameter KEY=Value`     Add a parameter. Repeat for multiple parameters
* `--tag KEY=Value`           Add a stack tag. Repeat for multipe tags
* `--capabilities CAPABILITY_IAM,CAPABILITY_NAMED_IAM`  Set one or multiple stack capabilities