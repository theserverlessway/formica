---
title: Modules
weight: 400
---

One of the core features of Formica is its module system. The goal is to make reusing existing CloudFormation components easy.

Modules are simply subfolders in the current directory. You can then either include all `template` files in that subfolder or include specific `template` files. All resources in the files you include will be automatically added to the template.

To load modules simply create a Resource with a FROM attribute in your existing `template` files. As with Resources you set a `LogicalName` to that instance of the Module (e.g. in the following example we're using SomeModule). This `LogicalName` can later be used to create multiple instances of the same module as its passed into the module as a variable. It also makes the module syntax feel more like a general CloudFormation resource and helps with naming parts of the template.

Example for including all `template` files in a subfolder:

```yaml
Resources:
  SomeModule:
    From: ModuleDirectory
```

```json
{
  "Resources": {
    "SomeModule": {
      "From": "ModuleDirectory"
    }
  }
}
```

This will automatically load all template files in the `moduledirectory` subfolder. Module directories and template files have to be lower cased and can't contain any whitespace. Otherwise they won't be found properly.

You can also use nested directories by separating them with `::` which follows the AWS Syntax for the types. The following example will load template from `submoduledirectory` in `moduledirectory`.


```yaml
Resources:
  SomeModule:
    From: ModuleDirectory::SubModuleDirectory
```

```json
{
  "Resources": {
    "SomeModule": {
      "From": "ModuleDirectory::SubModuleDirectory"
    }
  }
}
```

## Loading only specific templates

Sometimes you don't want to load the whole module folder, but only specific templates. You can do this by adding the template name at the end of the `From` field. So if you have a file `sometemplate.template.json` in a subfolder you just add  `::SomeTemplate` (upper/lower casing is irrelevant as we'll simply downcase). If you have multiple files that start with the template name, but have different extensions (e.g. `sometemplate.template.yaml` and `sometemplate.template.json`) all of them will be loaded.

Following is an example in yaml and json:

```yaml
Resources:
  SomeModule:
    From: ModuleDirectory::SomeTemplate
```

```json
{
  "Resources": {
    "SomeModule": {
      "From": "ModuleDirectory::SomeTemplate"
    }
  }
}
```

Formica will check if there is a folder named `sometemplate`, if that doesn't exist it will try to find template files with that name. Make sure you don't name folders and templates the same in case you want to include them separately as folders have precedence.

You can check out the [formica-modules](https://github.com/flomotlik/formica-modules) repository for official modules.

## Properties

Similar to CloudFormation Resources you can also pass Properties to the modules. In the following example we're creating a Route53 HostedZone for a domain and pass the domain, target and HostedZone to a the CName file in a DNS module.

```yaml
Resources:
  SomeCname:
    From: DNS::CName
    Properties:
      Source: flomotlik.me
      Target: somewhere.else.me
      HostedZone: FloMotlikHostedZone
```

In the module you can then use the variable:

```yaml
{{ module_name }}RecordSet:
  Type: AWS::Route53::RecordSet
  Properties:
    HostedZoneName:
      Ref: {{ HostedZone }}
    Name: {{ Source }}
    Type: CNAME
    TTL: '43200'
    ResourceRecords:
      - {{ Target }}
```

## Building reusable modules

If you want your modules to be used multiple times in one template (e.g. a module for DNS handling) you need to make sure to properly name and reference your resources. In the above example we've used `module_name` to create a name for the resource that is unique. The `module_name` variable is the `LogicalName` mentioned before that we're setting when configuring a module.

This makes sure that in the final CloudFormation template the Resources won't just be named `RecordSet` but `WWWRecordSet` for example if we create a cname for www.

You have to use the `module_name` variable in any case you're referencing a Resource in the module as well, e.g. if you're doing `!Ref RecordSet` you actually have to do `!Ref {{ module_name }}RecordSet`. For best reusability you should also think about creating Parametes in your Module instead of relying too much on variables. This makes sure that a module doesn't depend on any formica variables, but can be set up just as a template with Parameters.

For more examples check out the [formica-modules](https://github.com/flomotlik/formica-modules) repository.

## How to get modules

As modules are simply subfolders of the current directory you can use any tool to add them. If you're in a git repository [`git submodule`](https://git-scm.com/docs/git-submodule) or [`git subtree`](https://blogs.atlassian.com/2013/05/alternatives-to-git-submodule-git-subtree/) are a great way to set up modules.

In the following example we'll add the `formica-modules` module into your project:

```
git submodule add https://github.com/flomotlik/formica-modules modules/formica
```

You can then check out specific tags in that submodule so you're specific about which version of the modules you use.

But in the end the important part is that modules are just subfolders. So any way to add them as a subfolder will work great.