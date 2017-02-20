import cfnresponse


def handler(event, context):
    print(event)
    responseValue = 5
    responseData = {}
    responseData['Data'] = responseValue
    responseData['Reason'] = 'SomeTestReason'
    cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData, "CustomResourcePhysicalID")
