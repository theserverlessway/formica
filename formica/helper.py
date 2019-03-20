def name(*names):
    name = ''.join(map(lambda name: name.title(), names))
    name = ''.join(e for e in name if e.isalnum())
    return name


def collect_vars(args):
    variables = args.vars or {}
    if args.organization_variables:
        variables.update(accounts_and_regions())
    return variables


def accounts_and_regions():
    acc = aws_accounts()
    acc.update(aws_regions())
    return acc


def aws_regions():
    from formica.aws import AWS
    current_session = AWS.current_session()
    ec2 = current_session.client('ec2')
    regions = ec2.describe_regions()
    regions = [r['RegionName'] for r in regions['Regions']]
    return {'AWSRegions': regions}


def aws_accounts():
    from formica.aws import AWS
    current_session = AWS.current_session()
    organizations = current_session.client('organizations')
    sts = current_session.client('sts')
    orgs = organizations.list_accounts()
    accounts = [{'Id': a['Id'], 'Name': a['Name'], 'Email': a['Email']} for a in orgs['Accounts'] if
                a['Status'] == 'ACTIVE']
    account_id = sts.get_caller_identity()['Account']
    return {'AWSAccounts': accounts,
            'AWSSubAccounts': [a for a in accounts if a['Id'] != account_id]}


def main_account_id():
    from formica.aws import AWS
    sts = AWS.current_session().client('sts')
    identity = sts.get_caller_identity()
    return identity['Account']
