import boto3

# AWS clients
dynamodb = boto3.client('dynamodb')
translate = boto3.client('translate')
polly = boto3.client('polly')
s3 = boto3.client('s3')


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
    content_id = intent_request['currentIntent']['slots']['contentid']
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {
    }
    table = 'contents'
    bucket = '<YOUR BUCKET>'
    translate_language = 'pt'
    polly_language = 'pt-BR'
    voice = 'Vitoria'

    # DYNAMODB #
    content_json = dynamodb.query(
        TableName=table,
        KeyConditionExpression="#6a200 = :6a200",
        ExpressionAttributeNames={"#6a200": "content_id"},
        ExpressionAttributeValues={":6a200": {"S": content_id}}
    )

    if len(content_json['Items']) > 0:
        description = content_json['Items'][0]['description']['S']

        # TRANSLATE #
        translated_text = translate.translate_text(
            Text=description,
            SourceLanguageCode='en',
            TargetLanguageCode=translate_language
        )

        # POLLY #
        audio = polly.synthesize_speech(
            Engine='standard',
            OutputFormat='mp3',
            LanguageCode=polly_language,
            Text=translated_text['TranslatedText'],
            VoiceId=voice
        )

        # S3 #
        file = '{}-{}.mp3'.format(translate_language, content_id)
        s3.put_object(
            Bucket=bucket,
            Body=audio['AudioStream'].read(),
            ACL='public-read',
            Key=file
        )

        # DYNAMODB #
        dynamodb.update_item(
            TableName=table,
            Key={
                "content_id": {"S": content_id}
            },
            UpdateExpression="SET #d5240 = :d5240",
            ExpressionAttributeNames={"#d5240": "content_audio"},
            ExpressionAttributeValues={":d5240": {
                "S": 'https://{}.s3.amazonaws.com/{}'.format(bucket, file)}}
        )

        message = 'Thank you! I created the audio file, you can download here: https://{}.s3.amazonaws.com/{}'.format(
            bucket, file)
    else:
        message = 'Sorry! I could not find any content with this id.'

    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': message
        }
    )
