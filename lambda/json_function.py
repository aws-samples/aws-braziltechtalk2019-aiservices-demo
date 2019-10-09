import boto3
import json
import random
import string

# AWS clients
s3 = boto3.client('s3')
comprehend = boto3.client('comprehend')
transcribe = boto3.client('transcribe')
dynamodb = boto3.client('dynamodb')

table = 'contents'


def lambda_handler(event, context):
    # Initialization
    bucket = event['Records'][0]['s3']['bucket']['name']
    file = event['Records'][0]['s3']['object']['key']
    description = 'n/a'
    key_phrases = 'n/a'

    # downloading the video text
    video_text = s3.get_object(Bucket=bucket, Key=file)
    print(video_text)
    rawjson = video_text['Body'].read()
    parsedjson = json.loads(rawjson)
    text_transcribed = parsedjson['results']['transcripts'][0]['transcript']

    description = 'Video: {}'.format(text_transcribed)

    # COMPREHEND #
    language = comprehend.detect_dominant_language(
        Text=description
    )
    language = language['Languages'][0]['LanguageCode']

    kps_extracted = comprehend.detect_key_phrases(
        Text=description,
        LanguageCode=language
    )

    if len(kps_extracted['KeyPhrases']) > 0:
        key_phrases = ''
        for kp in kps_extracted['KeyPhrases']:
            key_phrases = key_phrases + kp['Text'] + ';'

    transcription_job = transcribe.get_transcription_job(
        TranscriptionJobName=file.split('.json', 1)[0]
    )

    # DYNAMODB #
    id_item = hash(file+''.join(
        [random.choice(string.ascii_letters + string.digits) for n in range(32)]))

    dynamodb.put_item(
        TableName=table,
        Item={
            'content_id': {'S': str(id_item)},
            'description': {'S': description.lower()},
            'key_phrases': {'S': key_phrases.lower()},
            'content_link': {'S': transcription_job['TranscriptionJob']['Media']['MediaFileUri']},
            'content_transcribe': {'S': 'https://{}.s3.amazonaws.com/{}'.format(bucket, file)}
        }
    )

    return {
        'statusCode': 200
    }
