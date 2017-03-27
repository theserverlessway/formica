class AWSBase(object):
    def __init__(self, session):
        self.session = session

    def cf_client(self):
        return self.session.client('cloudformation')
