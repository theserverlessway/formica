import cfnresponse


def handler(event, context):
    print(event)
    response_data = {}
    response_data['Data'] = 'DataResponse'
    response_data['Reason'] = 'SomeTestReason'
    cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data, "CustomResourcePhysicalID")
