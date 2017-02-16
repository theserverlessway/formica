# `formica change`

Through the change command you can upload your local template to CloudFormation and create a new Changeset. You can see the full template that will be used by running [`formica template`](template.md).

After the change was submitted a description of the changes will be printed. For all details of those changes check out the documentation for [`formica describe`](describe.md)

## Options

* `--stack STACK`             The stack to submit your changes to.  [required]
* `--profile PROFILE`         The AWS profile to use.
* `--region REGION`           The AWS region to use.
* `--parameter KEY=Value`     Add a parameter. Repeat for multiple parameters
* `--tag KEY=Value`           Add a stack tag. Repeat for multipe tags
* `--capabilities CAPABILITY_IAM,CAPABILITY_NAMED_IAM`  Set one or multiple stack capabilities