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
    from formica.aws import AWS
    current_session = AWS.current_session()
    organizations = current_session.client('organizations')
    ec2 = current_session.client('ec2')
    sts = current_session.client('sts')
    orgs = organizations.list_accounts()
    regions = ec2.describe_regions()
    accounts = [{'Id': a['Id'], 'Name': a['Name'], 'Email': a['Email']} for a in orgs['Accounts'] if
                a['Status'] == 'ACTIVE']
    regions = [r['RegionName'] for r in regions['Regions']]
    account_id = sts.get_caller_identity()['Account']
    return {'AWSAccounts': accounts, 'AWSRegions': regions,
            'AWSSubAccounts': [a for a in accounts if a['Id'] != account_id]}
