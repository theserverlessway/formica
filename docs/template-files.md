## Template file reference

Formica template files are simple python files with an `*.fc` extension. This means you can write any python code inside of the template files, but should be cautios.

## Available AWS Resources

Formica uses [Troposphere](https://github.com/cloudtools/troposphere) to compile `*.fc` files into CloudFormation templates.

All Troposphere modules that implement different AWS services are available in your template files without you having to import them specifically. For example you can use the following to create an S3 bucket that hosts static pages:

```python
resource(s3.Bucket(
    name(domain, 'Bucket'),
    BucketName= domain,
    AccessControl= s3.PublicRead,
    WebsiteConfiguration= s3.WebsiteConfiguration(
        IndexDocument='index.html'
    )
))
```

As you can see in this examples we have to prepend `s3.` for the different classes here. Formica only makes the modules directly available but not their respective classes because that might lead to clashes between different modules, e.g. different modules implement a `Tag` class.

To see all the different modules and classes available in troposphere check out [their modules](https://github.com/cloudtools/troposphere/tree/master/troposphere).

## Built-in functions

The following functions follow the [CloudFormation template anatomy docs](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-anatomy.html) to give you access to all the different parts of a template.

### name

The name function joins together all arguments and replaces any special characters. This is helpful for creating the resource LogicalId 

```python
variable = 'some.bucket'
resource(s3.Bucket(
    name(variable, 'Bucket')
))
```

will result in

```shell
{
    "Resources": {
        "SomeBucketBucket": {
            "Type": "AWS::S3::Bucket"
        }
    }
}
```

### resource

Add a Resource to the template:

```python
resource(s3.Bucket("TestName"))
```

### description

Set the description of the template:

```python
description("TestDescription")
```

### mapping

Add a mapping to the template

```python
mapping("RegionMap", {"us-east-1": {"AMI": "ami-7f418316"}})
```

## parameter

Add a parameter to the template

```python
parameter(Parameter("param", Type="String"))
```

## output

Add an Output to the template

```python
output(Output("Output", Value="value"))
```

## condition

Add a condition to the template

```python
condition("Condition1", Equals(Ref("EnvType"), "prod"))
```

## metadata

Add metadata to the template

```python
metadata({"key": "value", "key2": "value2"})
```