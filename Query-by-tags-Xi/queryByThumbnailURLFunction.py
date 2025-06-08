import json
import _helper as _
from models import BirdBaseModel

def lambda_handler(event, context):
    # TODO implement
    request_method = event.get("requestContext", {}).get("http", {}).get("method")
    if not request_method:
        request_method = event.get("httpMethod")
    print(f'request_method: {request_method}')

    thumbnail_url = ''    
    if request_method == "POST":
        # Handle POST request
        print("POST method")
        body = event.get("body")
        if not body:
            return _.build_response(400, {
                "message": "Error. No body provided."
            })

        try:
            parsed_body = json.loads(body)
            thumbnail_url = parsed_body.get("thumbnail")
        except json.JSONDecodeError:
            return _.build_response(400, {
                "message": "Error. Invalid JSON."
            })
        
    print(f'thumbnail_url: {thumbnail_url}')
     
    if not thumbnail_url:
        return _.build_response(400, {
            "message": "Error. No thumbnail URL provided."
        })
    
    # do some clean-up stuff for the url
    thumbnail_url = _.clean_url(thumbnail_url)
    print(f'Thumbnail after clean up: {thumbnail_url}')
    thumbnail_url = _.extract_s3_url(thumbnail_url)
    print(f'Thumbnail after extract: {thumbnail_url}')

    # do the query
    item = None 
    for item in BirdBaseModel.scan(BirdBaseModel.ThumbnailURL == thumbnail_url):
        if item:
            break
    print(f'result: {item}')

    if not item:
        return _.build_response(404, {
            "message": "Error. No matching thumbnail URL found.",
            "request_thumbnail_url": thumbnail_url
        })

    return _.build_response(200, {
        "message": f"The MediaURL found.",
        "requested_thumbnail_url": thumbnail_url,
        "results": {
            "MediaID": item.MediaID,
            "FileType": item.FileType,
            "MediaURL": _.generate_presigned_url(item.MediaURL),
            "ThumbnailURL": _.generate_presigned_url(item.ThumbnailURL),
            #    "UploadedDate": item.UploadedDate,
            "Uploader": item.Uploader
        }
    })
           