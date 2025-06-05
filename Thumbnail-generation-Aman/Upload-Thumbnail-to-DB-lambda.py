import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BirdBase')

def lambda_handler(event, context):
    # Get bucket and object key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Only process objects in the thumbnails/ folder
    if not key.startswith('thumbnails/'):
        return {'statusCode': 400, 'body': 'Not a thumbnail upload.'}

    # Extract the thumbnail file name
    thumbnail_name = os.path.basename(key)

    # Construct S3 URL
    s3_url = f"https://{bucket}.s3.us-east-1.amazonaws.com/{key}"

    # Store the file name and URL in DynamoDB
    table.put_item(Item={
        'BirdID': thumbnail_name,  # primary key
        'thumbnail_url': s3_url
    })

    return {
        'statusCode': 200,
        'body': f"Thumbnail URL stored in DynamoDB: {s3_url}"
    }