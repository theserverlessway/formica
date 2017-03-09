from boto3.session import Session


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
        params = {}
        if region:
            params['region_name'] = region
        if profile:
            params['profile_name'] = profile
        AWS.__session = Session(**params)
