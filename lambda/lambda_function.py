from models import FileModel
import uuid

def lambda_handler(event, context):
    try:
        # Simulate getting the media file data
        # from a previous triggered lambda function
        file_id = event.get('FileId')
        file_type = event.get('FileType')
        s3_url = event.get('S3URL')
        thumbnail_url = event.get('ThumbnailURL')
        file_tags = event.get('FileTags')

        # Missing ID or URL link
        if not file_id or not file_type or not s3_url:
            return {
                'statusCode': 400,
                'body': 'Missing required parameters'
            }
        
        # Create a FileModel object
        file = FileModel(
            FileId = file_id,
            FileType = file_type,
            S3URL = s3_url,
            ThumbnailURL = thumbnail_url,
            FileTags = file_tags
        )

        # Save to DynamoDB
        file.save()

        # Return the status
        return {
            'statusCode': 200,
            'body': 'File information saved successfully'
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }

    