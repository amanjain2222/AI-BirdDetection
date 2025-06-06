from models import BirdBaseModel, BirdBaseIndexModel
import uuid
import json

def lambda_handler(event, context):
    try:
        params = event.get("queryStringParameters", {}) or {}
        filter_tags = {}

        for species, count_str in params.items():
            try:
                # If count is missing or empty, treat as 1
                count = int(count_str) if count_str and count_str.strip() else 1
                # print(f'species_count: {count}')
                filter_tags[species] = count
            except ValueError:
                # Skip invalid count values
                continue

        if not filter_tags:
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "text/html"
                },
                "body": 
                    """
                    <html>
                        <head><title>Search Page</title></head>
                        <body>
                            <h1>Dummy Search Page</h1>
                            <p>To search, use a GET request with parameters like <code>?crow=2&owl=1</code></p>
                        </body>
                    </html>
                    """
            }

        matching_ids = None

        for species, min_count in filter_tags.items():
            # Query BirdBaseIndexModel for each tag
            result_ids = set()
            for item in BirdBaseIndexModel.query(species):
                if item.TagValue >= min_count:
                    result_ids.add(item.BirdID)
            
            # Intersect with previous results to satisfy all tag conditions
            if matching_ids is None:
                matching_ids = result_ids
            else:
                matching_ids &= result_ids

        if not matching_ids:
            return {
                "statusCode": 200,
                "body": json.dumps({"results": []})
            }

        # Retrieve media records from BirdBaseModel
        results = []
        for bird_id in matching_ids:
            item = BirdBaseModel.get(bird_id)
            results.append({
                "BirdID": item.BirdID,
                "FileType": item.FileType,
                "MediaURL": item.MediaURL,
                "ThumbnailURL": item.ThumbnailURL,
                "UploadedDate": item.UploadedDate,
                "Uploader": item.Uploader
            })

        print(results)

        return {
            "statusCode": 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',   # or your domain
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            "body": json.dumps({"results": results})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }

    