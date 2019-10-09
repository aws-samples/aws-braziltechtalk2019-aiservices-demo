import boto3
import random
import string

# AWS clients
textract = boto3.client('textract')
rekognition = boto3.client('rekognition')
comprehend = boto3.client('comprehend')
dynamodb = boto3.client('dynamodb')

table = 'contents'


def lambda_handler(event, context):
    # Initialization
    bucket = event['Records'][0]['s3']['bucket']['name']
    file = event['Records'][0]['s3']['object']['key']
    description = 'n/a'
    key_phrases = 'n/a'
    celebrity = 'n/a'

    # TEXTRACT #
    text_extracted = textract.detect_document_text(
        Document={
            'S3Object': {
                'Bucket': bucket,
                'Name': file
            }
        }
    )

    if len(text_extracted['Blocks']) > 0:
        description = ''
        for line in range(1, 5, 1):
            if text_extracted['Blocks'][line]['BlockType'] == 'LINE':
                description = description + \
                    text_extracted['Blocks'][line]['Text'] + ' '

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

    # REKOGNITION #
    celebrity_detected = rekognition.recognize_celebrities(
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': file
            }
        }
    )

    if len(celebrity_detected['CelebrityFaces']) > 0:
        celebrity = celebrity_detected['CelebrityFaces'][0]['Name']

    # DYNAMODB #
    id_item = hash(file+''.join(
        [random.choice(string.ascii_letters + string.digits) for n in range(32)]))

    dynamodb.put_item(
        TableName=table,
        Item={
            'content_id': {'S': str(id_item)},
            'description': {'S': description.lower()},
            'key_phrases': {'S': key_phrases.lower()},
            'celebrity': {'S': celebrity.lower()},
            'content_link': {'S': 'https://{}.s3.amazonaws.com/{}'.format(bucket, file)}
        }
    )

    return {
        'statusCode': 200
    }
