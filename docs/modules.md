## Module System

One of the core features of Formica is its module system. The goal is to make reusing existing CloudFormation components easy.

Modules are simply subfolders in the current directory. You can then either include all `*.fc` files in that subfolder or include specific `*.fc` files. All resources in the files you include will be automatically added to the template.

Example for including all `*.fc` files in a subfolder:

```python
module('bucket')
```

Example of including a specific `*.fc` file. You don't have to add the `.fc` extension:

```python
module('dns', 'cname')
```

You can check out the [formica-modules](https://github.com/flomotlik/formica-modules) repository for official modules. 

## Variables

You can also pass variables to the modules. In the following example we're creating a Route53 HostedZone for a domain and pass the domain, target and HostedZone to a the CName file in a DNS module.

```python
domain = 'cname.somedomain.me'
hostedZone = resource(route53.HostedZone(name(domain), Name=domain))
module('dns', 'cname', source=domain, target='somewhere.else.me', hostedZone=hostedZone)
```

In the module you can then use the variable:

```python
resource(route53.RecordSetType(
    name(source, "CNameRecord"), # using the built-in name function for filter unallowed characters
    Name= source,
    Type= 'CNAME',
    HostedZoneId= Ref(hostedZone),
    ResourceRecords= [target],
    TTL= 43200))
```

## How to get modules

As modules are simply subfolders of the current directory you can use any tool to add them. If you're in a git repository [`git submodule`](https://git-scm.com/docs/git-submodule) or [`git subtree`](https://blogs.atlassian.com/2013/05/alternatives-to-git-submodule-git-subtree/) are a great way to set up modules.

In the following example we'll add the `formica-modules` module into your project:

```shell
git submodule add https://github.com/flomotlik/formica-modules modules/formica
```

You can then check out specific tags in that submodule so you're specific about which version of the modules you use.

But in the end the important part is that modules are just subfolders. So any way to add them as a subfolder will work great.