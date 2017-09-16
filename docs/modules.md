## Module System

One of the core features of Formica is its module system. The goal is to make reusing existing CloudFormation components easy.

Modules are simply subfolders in the current directory. You can then either include all `template` files in that subfolder or include specific `template` files. All resources in the files you include will be automatically added to the template.

To load modules simply add a `Modules` config to your existing `template` files.

Example for including all `template` files in a subfolder:

```yaml
Modules:
  - path: moduledirectory
```

```json
{
	"Modules": [
		{
			"path": "moduledirectory"
		}
	]
}
```

Example of including a specific `template` file. Only add the part before `.template.(yaml|yml|json)`, so if you
have a file `something.template.json` in a subfolder you just set the template to `something`. If you have multiple
files that start with the template name, but have different extensions (e.g. `something.template.yaml` and `something.template.json`)
all of them will be loaded.

Following is an example in yaml and json:

```yaml
Modules:
  - path: moduledirectory
    template: sometemplate
```

```json
{
	"Modules": [
		{
			"path": "moduledirectory",
			"template": "sometemplate"
		}
	]
}
```

You can check out the [formica-modules](https://github.com/flomotlik/formica-modules) repository for official modules.

## Variables

You can also pass variables to the modules. In the following example we're creating a Route53 HostedZone for a domain and pass the domain, target and HostedZone to a the CName file in a DNS module.

```yaml
Modules:
  - path: dns
    template: cname
    vars:
      source: flomotlik.me
      target: somewhere.else.me
      hostedZone: FloMotlikHostedZone
```

In the module you can then use the variable:

```yaml
{{ source }}RecordSet:
  Type: AWS::Route53::RecordSet
  Properties:
    HostedZoneName:
      Ref: {{ hostedZone }}
    Name: {{ source }}
    Type: CNAME
    TTL: '43200'
    ResourceRecords:
      - {{ target }}
```

## How to get modules

As modules are simply subfolders of the current directory you can use any tool to add them. If you're in a git repository [`git submodule`](https://git-scm.com/docs/git-submodule) or [`git subtree`](https://blogs.atlassian.com/2013/05/alternatives-to-git-submodule-git-subtree/) are a great way to set up modules.

In the following example we'll add the `formica-modules` module into your project:

```
git submodule add https://github.com/flomotlik/formica-modules modules/formica
```

You can then check out specific tags in that submodule so you're specific about which version of the modules you use.

But in the end the important part is that modules are just subfolders. So any way to add them as a subfolder will work great.