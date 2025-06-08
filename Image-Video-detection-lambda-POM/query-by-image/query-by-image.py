import base64
import boto3
import cv2 as cv
import json
import os
import supervision as sv
from ultralytics import YOLO
import helpers as _
from models import BirdBaseModel, BirdBaseIndexModel


def count_items(input_list: list):
    """
    Counts the occurrences of each item in a list and returns a dictionary
    where keys are items converted to lowercase and values are their counts.
    """
    counts = {}
    for item in input_list:
        key = str(item).lower()
        counts[key] = counts.get(key, 0) + 1
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
            return _.build_response(400, {
                "message": "An error occurred while processing your request",
                "error": "No request body found"
            })

        # Parse JSON body to get base64 image data
        try:
            body = json.loads(event["body"])
        except json.JSONDecodeError:
            return _.build_response(400, {
                "message": "An error occurred while processing your request",
                "error": "Invalid JSON in request body"
            })

        # Extract base64 image data
        if "image" not in body:
            return _.build_response(400, {
                "message": "An error occurred while processing your request",
                "error": "No 'image' field found in request body"
            })

        print("Processing base64 encoded image data...")
        try:
            image_data = base64.b64decode(body["image"])
        except Exception as e:
            return _.build_response(400, {
                "message": "An error occurred while processing your request",
                "error": f"Invalid base64 image data: {str(e)}"
            })

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

        print(f"Retrived results: {results}")

        return _.build_response(200, {
            "message": f"Succeeded! Got {len(results)} records",
            "results": results
        })

    except Exception as e:
        return _.build_response(500, {
            "message": "An error occurred while processing your request",
            "error": str(e)
        })
