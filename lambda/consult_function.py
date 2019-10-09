import boto3

# AWS clients
dynamodb = boto3.client('dynamodb')


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def lambda_handler(event, context):
    # Initialization
    intent_request = event
    table = 'contents'
    value = intent_request['currentIntent']['slots']['keyword']
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {
    }

    # DYNAMODB #
    results = dynamodb.scan(
        TableName=table,
        FilterExpression="contains(#7c0c3, :7c0c3) Or contains(#7c0c4, :7c0c4)",
        ProjectionExpression="#7c0c0,#7c0c1,#7c0c2",
        ExpressionAttributeNames={"#7c0c0": "content_id", "#7c0c1": "description",
                                  "#7c0c2": "content_link", "#7c0c3": "key_phrases", "#7c0c4": "celebrity"},
        ExpressionAttributeValues={":7c0c3": {
            "S": value}, ":7c0c4": {"S": value}}
    )

    item = ''

    if len(results['Items']) > 0:
        message = '<p>I found some content! Look what I have:</p>'
        for item in results['Items']:
            message = message + '<li><p><b>id = {}</b></p><p>Short description: {}</p><p>Download: {}</p></li>'.format(
                item['content_id']['S'], item['description']['S'], item['content_link']['S'])
            print(item)
        message = message + '<p> If you want, I can generate the audio file of the content in portuguese. Just say the content id for me!</p>'

    else:
        message = '<p>Sorry! I could not find anything. Try to upload a new file.</p>'

    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': message
        }
    )
