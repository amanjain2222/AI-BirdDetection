import json
import boto3
import uuid
import random
import os
from datetime import datetime, timedelta
from models import BirdBaseModel, BirdBaseIndexModel

dynamodb = boto3.resource('dynamodb')
base_table = dynamodb.Table('BirdBase')
index_table = dynamodb.Table('BirdBaseIndex')

def generate_tags(media_records):
    species = ["crow", "sparrow", "eagle", "parrot", "pigeon", "owl", "duck", "canary", "finch"]
    results = []
    
    for record in media_records:
        media_id = record['MediaID']
        for species_name in species:
            species_count = 0
            for _ in range(random.randint(0, 20)):
                if random.random() < 0.3:  # Randomly decide if this species is present in the record
                    species_count += 1
            if species_count > 0:
                results.append({
                    "TagName": species_name,
                    "TagValue": species_count,
                    "MediaID": media_id
                })
    return results

def random_date(start_date, end_date):
    """
    Generate a random datetime between two datetime objects.
    
    Args:
        start_date (datetime): The start of the range.
        end_date (datetime): The end of the range.
        
    Returns:
        datetime: A random datetime between start_date and end_date.
    """
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, 86400 - 1)  # seconds in a day
    return start_date + timedelta(days=random_days, seconds=random_seconds)

def generate_media_record():
    file_id = str(uuid.uuid4())
    file_type = random.choice(['image', 'video', 'audio'])

    extension = ''
    thumbnail_url = ''
    if file_type == 'image':
        extension = 'jpg'
        thumbnail_url = f"https://dummy-bucket.s3.amazonaws.com/thumbnails/{file_id}.{extension}"
    elif file_type == 'video':
        extension = 'mp4'
    else:
        extension = 'mp3'

    if not extension:
        raise ValueError("Invalid file type")
    
    # tags = generate_tags()
    start_date = datetime(2024, 1, 1)
    end_date = datetime.now()

    # uploaded_date = random_date(start_date, end_date)

    return {
        "MediaID": file_id,
        "FileType": file_type,
        "MediaURL": f"https://dummy-bucket.s3.amazonaws.com/images/{file_id}.{extension}",
        "ThumbnailURL": thumbnail_url,
    #    "UploadedDate": uploaded_date,
        "Uploader": f"user_{random.randint(1, 100)}",
    }

def generate_media_set(count):
    items = []
    for _ in range(count):
        item = generate_media_record()
        items.append(item)
    return items

def lambda_handler(event, context):
    bird_base_rows = generate_media_set(random.randint(10, 30))
    
    bird_base_index_rows = generate_tags(bird_base_rows)

    # print(f'media set: {bird_base_rows}')
    # print(f'index set: {bird_base_index_rows}')

    # Save BirdBase rows to DynamoDB
    for item in bird_base_rows:
        BirdBaseModel(
            MediaID=item["MediaID"],
            FileType=item["FileType"],
            MediaURL=item["MediaURL"],
            ThumbnailURL=item["ThumbnailURL"],
        #    UploadedDate=item["UploadedDate"].isoformat(),  # Convert datetime to string
            Uploader=item["Uploader"]
        ).save()

    # Save BirdBaseIndex rows to DynamoDB
    for tag in bird_base_index_rows:
        BirdBaseIndexModel(
            TagName=tag["TagName"],
            TagValue=tag["TagValue"],
            MediaID=tag["MediaID"]
        ).save()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Media records and tags generated successfully",
            "media_count": len(bird_base_rows),
            "index_count": len(bird_base_index_rows)
        })
    }
