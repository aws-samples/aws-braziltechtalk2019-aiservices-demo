import boto3
import random
import string

# AWS clients
transcribe = boto3.client('transcribe')


def lambda_handler(event, context):
    # Initialization
    bucket = event['Records'][0]['s3']['bucket']['name']
    file = event['Records'][0]['s3']['object']['key']

    transcription_job = ''.join(
        [random.choice(string.ascii_letters + string.digits) for n in range(32)])

    # TRANSCRIBE #
    transcribe.start_transcription_job(
        TranscriptionJobName=str(hash(file+transcription_job)),
        LanguageCode='en-US',
        MediaFormat='mp4',
        Media={
            'MediaFileUri': 'https://{}.s3.amazonaws.com/{}'.format(bucket,
                                                                    file)
        },
        OutputBucketName=bucket
    )

    return {
        'statusCode': 200
    }
