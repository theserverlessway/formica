---
title: Working with Stack Sets
weight: 600
---

Stack sets are a fantastic way to manage infrastructure across multiple accounts using CloudFormation. Formica allows you to use the same template building features you're accustomed to with Stacks to use for StackSets. It also gives you all the commands necessary to manage your StackSet instances and update your StackSets.

You can see all the available StackSet commands by running `formica stack-set --help`.

Let's go through a quick example how to use it:

In the example we're creating an AWS Config Recorder across all your accounts and regions. The following template would configure that Recorder and a Role to access all necessary resources.


```
Resources:
  ConfigurationRecorderGlobal:
    Type: 'AWS::Config::ConfigurationRecorder'
    Properties:
      RecordingGroup:
        AllSupported: true
        IncludeGlobalResourceTypes: true
      RoleARN: !GetAtt 'ConfigurationRecorderRole.Arn'

  ConfigurationRecorderRole:
    Type: 'AWS::IAM::Role'
    Properties:
      ManagedPolicyArns:
      - 'arn:aws:iam::aws:policy/service-role/AWSConfigRole'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
        - Sid: AssumeRole
          Effect: Allow
          Principal:
            Service: 'config.amazonaws.com'
          Action: 'sts:AssumeRole'
```

You can use the same commands like `formica template` to see the resulting template before pushing it to CloudFormation.

To deploy the stack consistently we're creating a config file as well (`stack-set.config.yaml` would be the typical name):

```
stack-set: config-recorder
capabilities:
  - CAPABILITY_IAM
```

With this in place we can now create the StackSet before adding instances to it.

```
formica stack-set create -c stack-set.config.yaml
```

Now we can add instances to it. You have to set the accounts and regions you want a specific stack-set action to be performed in for every command or through the config file. CloudFormation will then update each individual stack in each account and region combination.

As a first step lets add us-east-1 in our main account.

```
formica stack-set add-instances -c stack-set.config.yaml --regions us-east-1 --main-account
```

As you can see we're not specifying the account id directly (but you can with `--accounts`, but using the --main-account option which means the account we're currently using. Formica will compare the currently deployed instances to the ones you want to add and give you a list of stacks it will actually create (or tell you if all were already added).

If you deploy to multiple accounts it will even figure out which account/region combinations overlap and deploy those as one action to enable parallelisation across accounts. CloudFormation will fail if you try to add an already existing instance, so we have to be careful to only add the specific ones that aren't already there.

Now lets add it to all subaccounts. All command line options have equivalent config file options which I'll show at the end of the post:

```
formica stack-set add-instances -c stack-set.config.yaml --regions us-east-1 --all-subaccounts
```

The same process as before will happen, you'll get a list of all instances to be added and the instances will be deployed.

Now let's add the configuration to deploy AWS Config everywhere into our configuration file.

```
stack-set: config-recorder
capabilities:
  - CAPABILITY_IAM
all-regions: true
all-accounts: true
```

And add the instances:

```
formica stack-set add-instances -c stack-set.config.yaml
```

Now if we want to update our StackSet Instances we can run the update command. It accepts the same account and region options as `add-instances`. Before the deployment it will also show you a diff of the currently deployed template and the new one. You can see the same diff with `formica stack-set diff -c stack-set.config.yaml`.

```
formica stack-set update -c stack-set.config.yaml.
```

The update, as all the other commands before, waits for the CloudFormation StackSet operation to finish and report the result. Stopping the command with `ctrl-c` will not end the operation though, just the waiter.

To remove StackSets, e.g. `eu-central-1` and `us-east-1` in the main account we can use the command `formica stack-set remove-instances -c stack-set.config.yaml --main-account --regions us-east-1 eu-central-1`.

If you want to remove a StackSet (after removing all its instances) you can run `formica stack-set remove -c stack-set.config.yaml`.

Check out all the existing formica commands in the [commands documentation]({{< relref "/tools/formica/commands" >}}) and run `--help` on any command you'd like to get additional info on in your workflow.