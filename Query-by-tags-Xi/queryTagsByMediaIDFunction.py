import json
import _helper as _
from models import BirdBaseModel, BirdBaseIndexModel

def lambda_handler(event, context):
    # TODO implement
    request_method = event.get("requestContext", {}).get("http", {}).get("method")
    if not request_method:
        request_method = event.get("httpMethod")
    
    if request_method == "GET":
        params = event.get("queryStringParameters", {})
        media_id = params.get("media_id", "")
        
        if not media_id:
            return _.build_response(400, {
                "message": "Error. A MediaID is required"
            })
        print(f"MediaID: {media_id}")
        
        try:
            media_tags = []
            for item in BirdBaseIndexModel.scan(BirdBaseIndexModel.MediaID == media_id):
                media_tags.append({
                    "TagName": item.TagName,
                    "TagValue": item.TagValue,
                    "MediaID": item.MediaID
                })
            return _.build_response(200, {
                "message": "Success. Tags retrieved",
                "results": media_tags
            })

        except Exception as e:
            print(e)
            return _.build_response(500, {
                "message": "Error. Could not retrieve tags"
            })

    return _.build_response(400, {
        "message": "Error. Invalid request method"
    })


