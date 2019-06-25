import urllib.request

def handler(event, context):
    result = {}
    print(event)
    contents = urllib.request.urlopen("http://theserverlessway.com").read()
    if event.get('num') is not None:
        print('Adding to Result')
        result['num'] = int(event['num']) + 1
    else:
        print('Setting 0')
        result['num'] = 0
    print('Result is: {}'.format(result))
    return result
