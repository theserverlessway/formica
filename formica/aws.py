class AWS:
    __session = None

    @staticmethod
    def current_session():
        if not AWS.__session:
            raise AttributeError('Session was not initialised')
        return AWS.__session

    def __init__(self):
        raise Exception('AWS Constructur should not be called')

    @staticmethod
    def initialize(region='', profile=''):
        from botocore import credentials
        import botocore.session
        import os

        cli_cache = os.path.join(os.path.expanduser('~'), '.aws/cli/cache')

        params = {}
        if profile:
            params['profile'] = profile

        session = botocore.session.Session(**params)
        session.get_component('credential_provider').get_provider('assume-role').cache = credentials.JSONFileCache(
            cli_cache)

        from boto3.session import Session
        params = {}
        if region:
            params['region_name'] = region

        AWS.__session = Session(botocore_session=session, **params)
