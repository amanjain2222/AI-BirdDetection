from models import BirdBaseModel, BirdBaseIndexModel
import uuid
import json
import boto3
import _helper as _

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        params = event.get("queryStringParameters", {}) or {}
        filter_tags = {}

        for species, count_str in params.items():
            try:
                species = species.lower()
                # If count is missing or empty, treat as 1
                count = int(count_str) if count_str and count_str.strip() else 1
                # print(f'species_count: {count}')
                filter_tags[species] = count
            except ValueError:
                # Skip invalid count values
                continue

        if not filter_tags:
            return _.build_response(200, {
                "message": "To search, use a GET request with parameters like ?crow=2&owl=1"
            })
             
        matching_ids = None

        for species, min_count in filter_tags.items():
            # Query BirdBaseIndexModel for each tag
            result_ids = set()
            for item in BirdBaseIndexModel.query(species):
                if item.TagValue >= min_count:
                    result_ids.add(item.MediaID)
                    result_ids.add(item.MediaID)
            
            # Intersect with previous results to satisfy all tag conditions
            if matching_ids is None:
                matching_ids = result_ids
            else:
                matching_ids &= result_ids

        if not matching_ids:
            return _.build_response(200, {
                "message": "No results found",
                "results": []
            })
            
        # Retrieve media records from BirdBaseModel
        results = []
        for media_id in matching_ids:
            item = BirdBaseModel.get(media_id)
        for media_id in matching_ids:
            item = BirdBaseModel.get(media_id)
            results.append({
                "MediaID": item.MediaID,
                "FileType": item.FileType,
                "MediaURL": _.generate_presigned_url(item.MediaURL, s3),
                "ThumbnailURL": _.generate_presigned_url(item.ThumbnailURL, s3),
            #    "UploadedDate": item.UploadedDate,
                "Uploader": item.Uploader
            })

        print(results)

        return _.build_response(200, {
            "message": f"Succeeded! Got {len(results)} records",
            "results": results
        })
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
            },
            "body": str(e)
        }

    