import json
import boto3
import uuid
import os

s3 = boto3.client('s3')
BUCKET_NAME = 'assignment3-51-bucket'

def lambda_handler(event, context):
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST',
            },
            'body': ''
        }

    try:
        data = json.loads(event['body'])
        file_name = data.get('file_name', 'file.unknown')

        _, file_extension = os.path.splitext(file_name)
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        folder = 'audio' if file_extension.lower() == '.wav' else 'images'
        s3_key = f"{folder}/{unique_filename}"

        # Generate pre-signed URL
        url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': s3_key,
                'ContentType': data.get('content_type', 'application/octet-stream')
            },
            ExpiresIn=300  # URL valid for 5 minutes
        )

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST',
            },
            'body': json.dumps({
                'upload_url': url,
                's3_key': s3_key,
                'file_name': unique_filename
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST',
            },
            'body': json.dumps(f"Error generating URL: {str(e)}")
        }