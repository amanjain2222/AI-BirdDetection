import json
import boto3
import uuid
import os

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
BUCKET_NAME = 'birdstore'
TABLE_NAME = 'BirdBase' 

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
        user_id = data.get('userID', None)   # Default to None, so we can check for it

        # Reject if no user ID token provided
        if not user_id:
            return {
                'statusCode': 401,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST',
                },
                'body': json.dumps('Unauthorized: Missing user ID token')
            }

        _, file_extension = os.path.splitext(file_name)
        unique_id = str(uuid.uuid4())
        unique_filename = f"{unique_id}{file_extension}"

        audio_extensions = ['.wav', '.mp3', '.m4a']
        video_extensions = ['.mp4', '.mov', '.avi']
        image_extensions = ['.jpg', '.png']

        # Determine folder and file type
        if file_extension.lower() in audio_extensions:
            folder = 'audio'
            file_type = 'audio'
        elif file_extension.lower() in video_extensions:
            folder = 'videos'
            file_type = 'video'
        elif file_extension.lower() in image_extensions:
            folder = 'images'
            file_type = 'image'
        else: 
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST',
                },
                'body': json.dumps('Unsupported file type')
            }

        s3_key = f"{folder}/{unique_filename}"

        # Generate pre-signed URL for upload
        upload_url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': s3_key,
                'ContentType': data.get('content_type', 'application/octet-stream')
            },
            ExpiresIn=300  # URL valid for 5 minutes
        )

        # Construct permanent S3 media URL
        media_url = f"https://{BUCKET_NAME}.s3.us-east-1.amazonaws.com/{s3_key}"

        # Store in DynamoDB
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(Item={
            'MediaID': unique_id,
            'FileType': file_type,
            'MediaURL': media_url,
            'ThumbnailURL': "",
            'Uploader': user_id
        })

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST',
            },
            'body': json.dumps({
                'upload_url': upload_url,
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
