from .s3 import temporary_bucket


def name(*names):
    name = "".join(map(lambda name: name.title(), names))
    name = "".join(e for e in name if e.isalnum())
    return name


def collect_stack_set_vars(args):
    variables = args.vars or {}
    if args.organization_variables:
        variables.update(accounts_and_regions())
    else:
        if args.organization_region_variables:
            variables.update(aws_regions())
        if args.organization_account_variables:
            variables.update(aws_accounts())

    return variables


def collect_vars(args):
    variables = collect_stack_set_vars(args)
    if args.artifacts:
        variables.update(artifact_variables(args.artifacts, vars(args).get("stack", "")))

    return variables


def accounts_and_regions():
    acc = aws_accounts()
    acc.update(aws_regions())
    return acc


def aws_regions():
    import boto3

    ec2 = boto3.client("ec2")
    regions = ec2.describe_regions()
    regions = [r["RegionName"] for r in regions["Regions"]]
    return {"AWSRegions": regions}


def aws_accounts():
    import boto3

    organizations = boto3.client("organizations")
    sts = boto3.client("sts")

    paginator = organizations.get_paginator("list_accounts")

    pages = paginator.paginate()
    accounts = [
        {"Id": a["Id"], "Name": a["Name"], "Email": a["Email"]}
        for page in pages
        for a in page["Accounts"]
        if a["Status"] == "ACTIVE"
    ]
    account_id = sts.get_caller_identity()["Account"]
    return {
        "AWSMainAccount": [a for a in accounts if a["Id"] == account_id][0],
        "AWSAccounts": accounts,
        "AWSSubAccounts": [a for a in accounts if a["Id"] != account_id],
    }


def main_account_id():
    import boto3

    sts = boto3.client("sts")
    identity = sts.get_caller_identity()
    return identity["Account"]


def artifact_variables(artifacts, seed):
    class Artifact:
        def __init__(self, key, bucket):
            self.key = key
            self.bucket = bucket

    artifact_keys = {}
    with temporary_bucket(seed=seed) as t:
        for a in artifacts:
            artifact_keys[a] = t.add_file(a)
        finished_vars = {key: Artifact(value, t.name) for key, value in artifact_keys.items()}
    return {"artifacts": finished_vars}


def with_artifacts(function):
    def handle_artifacts(args):
        if args.artifacts:
            seed = vars(args).get("stack", "")
            with temporary_bucket(seed=seed) as t:
                for a in args.artifacts:
                    t.add_file(a)
                t.upload()
                function(args)
        else:
            function(args)

    return handle_artifacts
