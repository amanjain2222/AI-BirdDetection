import json
import boto3
from models import BirdBaseModel, BirdBaseIndexModel
from pynamodb.exceptions import DoesNotExist
import _helper as _

s3 = boto3.client('s3')

def lambda_handler(event, context):
    request_method = event.get("requestContext", {}).get("http", {}).get("method")
    if not request_method:
        request_method = event.get("httpMethod")
    print(f'request_method: {request_method}')

    if request_method != "DELETE":
        return _.build_response(400, {
            "message": "This endpoint only accepts DELETE-methods",
            "current_request_method": request_method
        })

    body = json.loads(event.get('body', '{}'))
    urls = body.get("urls", [])
    print(f'urls: {urls}')

    if not urls:
        return _.build_response(400, {
            "message": "No media URLs provided.",
            "current_request_method": request_method
        })

    deleted_items = []

    for url in urls:
        url = _.clean_url(url)
        url = _.extract_s3_url(url)
        
        # Find the record in BirdBaseModel by MediaURL
        for item in BirdBaseModel.scan(BirdBaseModel.MediaURL == url):
            # Delete related BirdBaseIndex entries
            try:
                
                for index_record in BirdBaseIndexModel.scan(BirdBaseIndexModel.MediaID == item.MediaID):
                    index_record.delete()
            except DoesNotExist:
                print(f"No BirdBaseIndexModel record found for MediaID: {item.MediaID}")

            # Delete file from S3
            try:
                bucket, key = _.parse_s3_url(item.MediaURL)
                if item.FileType == 'image':
                    thumbnail_bucket, thumbnail_key = _.parse_s3_url(item.ThumbnailURL)
                    s3.delete_object(Bucket=thumbnail_bucket, Key=thumbnail_key)
                    print(f'Deleted {thumbnail_key} from S3 bucket {thumbnail_bucket}')
                s3.delete_object(Bucket=bucket, Key=key)
            except Exception as e:
                print(f"Error deleting file from S3: {e}")

            # Mark down the MediaID of the files 
            deleted_items.append(item.MediaID)
            
            # Delete main record
            try:
                item.delete()
            except DoesNotExist:
                print(f"No BirdBaseModel record found for MediaID: {item.MediaID}")
                        

    return _.build_response(200, {
        "message": f"{len(deleted_items)} media file(s) got deleted successfully.",
        "deleted": deleted_items
    })