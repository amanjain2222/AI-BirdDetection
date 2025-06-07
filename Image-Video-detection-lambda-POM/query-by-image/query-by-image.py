import base64
import boto3
import cv2 as cv
import json
import os
import supervision as sv
from ultralytics import YOLO
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute


class BirdBaseModel(Model):
    class Meta:
        table_name = "BirdBase"
        region = "us-east-1"
        read_capacity_units = 1
        write_capacity_units = 1

    # Primary key
    MediaID = UnicodeAttribute(hash_key=True)

    # File type: image, video or audio
    FileType = UnicodeAttribute()

    # Link to the file in S3
    MediaURL = UnicodeAttribute()

    # Link to the image thumbnail
    ThumbnailURL = UnicodeAttribute(null=True)

    # Uploaded date
    # UploadedDate = UnicodeAttribute()

    # Uploader's username
    Uploader = UnicodeAttribute()


class BirdBaseIndexModel(Model):
    class Meta:
        table_name = "BirdBaseIndex"
        region = "us-east-1"
        read_capacity_units = 1
        write_capacity_units = 1

    # Primary key
    TagName = UnicodeAttribute(hash_key=True)

    # Number of a specific species
    TagValue = NumberAttribute()

    # UUID of the media file
    MediaID = UnicodeAttribute(range_key=True)


def count_items(input_list: list):
    """
    Counts the occurrences of each item in a list and returns a dictionary
    where keys are items and values are their counts.
    """
    counts = {}
    for item in input_list:
        counts[item] = counts.get(item, 0) + 1
    return counts


def image_prediction(image_path: str, model_path: str, confidence: float = 0.5):
    """
    Function to make predictions of a pre-trained YOLO model on a given image.

    Parameters:
        image_path (str): Path to the image file. Can be a local path or a URL.
        model_path (str): path to the model.
        confidence (float): 0-1, only results over this value are saved.
    """
    # Load YOLO model
    model = YOLO(model_path)
    class_dict = model.names

    # Load image from local path
    img = cv.imread(image_path)

    # Check if image was loaded successfully
    if img is None:
        print("Couldn't load the image! Please check the image path.")
        return []

    # Run the model on the image
    result = model(img)[0]

    # Convert YOLO result to Detections format
    detections = sv.Detections.from_ultralytics(result)

    tags = []
    # Filter detections based on confidence threshold and check if any exist
    if detections.class_id is not None:
        detections = detections[(detections.confidence > confidence)]

        # Create tags for the detected objects
        tags = [
            f"{class_dict[cls_id]}"
            for cls_id, _ in zip(detections.class_id, detections.confidence)
        ]

    return tags


def lambda_handler(event, context):
    model_temp_path = None
    img_temp_path = None

    try:
        # Get environment variables
        model_bucket = os.environ.get("MODEL_BUCKET_NAME", "birdstore")
        model_key = os.environ.get("MODEL_KEY", "models/model.pt")
        confidence_threshold = float(os.environ.get("CONFIDENCE_THRESHOLD", "0.5"))

        print(f"Using model bucket: {model_bucket}")
        print(f"Using model key: {model_key}")
        print(f"Using confidence threshold: {confidence_threshold}")

        s3 = boto3.client("s3")

        # Download model
        print("Downloading model from S3...")
        model_temp_path = f"/tmp/model_{context.aws_request_id}_{os.path.basename(model_key)}"
        s3.download_file(model_bucket, model_key, model_temp_path)

        # Process base64 encoded image from request
        if not event.get("body"):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No request body found"}),
            }

        # Parse JSON body to get base64 image data
        try:
            body = json.loads(event["body"])
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid JSON in request body"}),
            }

        # Extract base64 image data
        if "image" not in body:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No 'image' field found in request body"}),
            }

        print("Processing base64 encoded image data...")
        try:
            image_data = base64.b64decode(body["image"])
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Invalid base64 image data: {str(e)}"}),
            }

        # Save image data to temporary file
        print("Saving image data to temporary file...")

        img_temp_path = f"/tmp/img_{context.aws_request_id}"

        with open(img_temp_path, "wb") as f:
            f.write(image_data)

        print("Making predictions...")
        tags = image_prediction(img_temp_path, model_temp_path, confidence_threshold)

        # Convert tags
        filter_tags = count_items(tags) if tags else {}
        
        print(f"Detected tags: {filter_tags}")

        # Query database for each detected species
        matching_ids = None
        for species, min_count in filter_tags.items():
            try:
                # Query BirdBaseIndexModel for each tag
                result_ids = set()
                for item in BirdBaseIndexModel.query(species):
                    if item.TagValue >= min_count:
                        result_ids.add(item.MediaID)

                print(f"Found {len(result_ids)} matches for {species} with count >= {min_count}")

                # Intersect with previous results to satisfy all tag conditions
                if matching_ids is None:
                    matching_ids = result_ids
                else:
                    matching_ids &= result_ids
                    
            except Exception as e:
                print(f"Error querying for species {species}: {e}")
                continue

        # If no matching IDs found, return empty results
        if not matching_ids:
            print("No matching media found")
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "results": [],
                    "detected_species": list(filter_tags.keys()),
                    "message": "No matching media found in database"
                })
            }

        print(f"Found {len(matching_ids)} total matching medias")

        # Retrieve media records from BirdBaseModel
        results = []
        for media_id in matching_ids:
            try:
                print(f"Getting media_id: {media_id}")
                item = BirdBaseModel.get(media_id)
                results.append({
                    "MediaID": item.MediaID,
                    "FileType": item.FileType,
                    "MediaURL": item.MediaURL,
                    "ThumbnailURL": item.ThumbnailURL,
                    # "UploadedDate": item.UploadedDate,
                    "Uploader": item.Uploader,
                })
            except Exception as e:
                print(f"Error retrieving media {media_id}: {e}")
                continue

        return {
            "statusCode": 200,
            "body": json.dumps({
                "results": results,
                "detected_species": list(filter_tags.keys()),
                "total_matches": len(results)
            }),
        }

    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Error query by image: {str(e)}"}),
        }
