import base64
import boto3
import mimetypes
import json

s3 = boto3.client('s3')
BUCKET_NAME = 'assignment3-51-bucket' 

def lambda_handler(event, context):
    try:
        data = json.loads(event['body'])

        file_name = data.get('file_name', 'file.unknown')
        file_data = base64.b64decode(data['file_data'])

        content_type, _ = mimetypes.guess_type(file_name)
        if not content_type:
            content_type = 'application/octet-stream'  # Fallback default

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"original/{file_name}",
            Body=file_data,
            ContentType=content_type
        )

        return {
            'statusCode': 200,
            'body': f"File {file_name} uploaded successfully to S3 bucket {BUCKET_NAME}"
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }