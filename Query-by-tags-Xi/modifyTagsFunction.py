import json
from urllib.parse import urlparse
from models import BirdBaseModel, BirdBaseIndexModel
from pynamodb.exceptions import DoesNotExist
import _helper as _

def parse_tags(tags):
    SPLITTER = ","
    modified_tags = []
    if not tags:
        return modified_tags
    
    for tag in tags:
        # tag format should be "crow,1"
        if type(tag) == str and tag.count(SPLITTER) == 1:
            tag_name = tag.split(SPLITTER)[0]
            tag_count = tag.split(SPLITTER)[1]
            if tag_name.isalpha() and tag_count.isdigit():
                tag_count = int(tag_count)
                if tag_count > 0:
                    modified_tags.append({tag_name: tag_count})
    return modified_tags

def find_media_by_thumbnail(thumbnail_urls, uploader = ""):
    media_ids = []
    for thumbnail_url in thumbnail_urls:
        thumnail_url = _.clean_url(thumbnail_url)
        thumbnail_url = _.extract_s3_url(thumbnail_url)
        for item in BirdBaseModel.scan(BirdBaseModel.ThumbnailURL == thumbnail_url):
            media_ids.append(item.MediaID)
    return media_ids

def add_tags_to_media_files(media_ids, tags):
    for media_id in media_ids:
        for each_tag in tags:
            for tag_name in each_tag:
                tag_value = each_tag[tag_name]
                # replace
                try:
                    item = BirdBaseIndexModel.get(tag_name, media_id)
                    item.TagValue = tag_value
                    item.save()
                # add
                except DoesNotExist:
                    BirdBaseIndexModel(
                        TagName = tag_name,
                        MediaID = media_id,
                        TagValue = tag_value
                    ).save()

def remove_tags_from_media_files(media_ids, tags):
    for media_id in media_ids:
        for each_tag in tags:
            for tag_name in each_tag:
                tag_value = each_tag[tag_name]
                try:
                    item = BirdBaseIndexModel.get(tag_name, media_id)
                    item.delete()
                except DoesNotExist:
                    continue

def lambda_handler(event, context):
    request_method = event.get("requestContext", {}).get("http", {}).get("method")
    if not request_method:
        request_method = event.get("httpMethod")
    print(f'request_method: {request_method}')

    if request_method != "POST":
        return _.build_response(400, {
            'message': 'Only POST requests are allowed',
            'current_request_method': request_method
        })

    try:
        # parse the body 
        parsed_body = json.loads(event.get("body"))
        print(f'parsed_body: {parsed_body}')

        urls = parsed_body.get("urls", [])
        tags = parsed_body.get("tags", [])
        operation = parsed_body.get("operation", -1)
        
        print(f"urls: {urls}")
        print(f"tags: {tags}")

        if not urls:
            return _.build_response(400, {
                'message': 'No thumbnail URLs provided in the request body',
                'current_urls': urls
            })
        
        if not tags:
            return _.build_response(400, {
                'message': 'No tags provided in the request body',
                'current_tags': tags
            })
        
        if operation not in [0, 1]:
            return _.build_response(400, {
                'message': 'Invalid operation provided in the request body. 1 for add and 0 for remove',
                'current_operation': operation
            })

        parsed_tags = parse_tags(tags)
        media_ids = find_media_by_thumbnail(urls)

        print(f'parsed_tags: {parsed_tags}')
        print(f'media_ids: {media_ids}')

        # add tags logic block
        if operation == 1:
            add_tags_to_media_files(media_ids, parsed_tags)

        # delete tags logic block
        elif operation == 0:
            remove_tags_from_media_files(media_ids, parsed_tags)

        return _.build_response(200, {
            'message': f'Tags in {len(media_ids)} file(s) modified successfully',
        })
    
    except Exception as e:
        return _.build_response(500, {
            'message': 'Internal server error',
            'error': str(e)
        })

