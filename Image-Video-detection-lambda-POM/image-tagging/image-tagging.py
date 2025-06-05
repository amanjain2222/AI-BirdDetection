import boto3
import cv2 as cv
import os
import supervision as sv
from ultralytics import YOLO


def count_items(input_list: list):
    """
    Counts the occurrences of each item in a list and returns a dictionary
    where keys are items and values are their counts.
    """
    counts = {}
    for item in input_list:
        counts[item] = counts.get(item, 0) + 1
    return counts


def update_items(prev_list: dict, curr_list: dict):
    """
    Updates prev_list with items from curr_list, adding new keys or
    updating existing keys only if the new value is greater.
    """
    for key, value in curr_list.items():
        # add to dict if key not exist
        if key not in prev_list:
            prev_list[key] = value
        # update to a higher value
        else:
            if value > prev_list[key]:
                prev_list[key] = value


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
        table_name = os.environ.get("DYNAMODB_TABLE_NAME", "BirdBaseIndex")
        model_bucket = os.environ.get("MODEL_BUCKET_NAME", "birdstore")
        model_key = os.environ.get("MODEL_KEY", "models/model.pt")

        print(f"Using DynamoDB table: {table_name}")
        print(f"Using model bucket: {model_bucket}")
        print(f"Using model key: {model_key}")

        s3 = boto3.client("s3")
        dynamodb = boto3.resource("dynamodb")

        # Get DynamoDB table
        table = dynamodb.Table(table_name)

        # Download model
        print("Downloading model from S3...")
        model_temp_path = f"/tmp/model_{context.aws_request_id}.pt"
        s3.download_file(model_bucket, model_key, model_temp_path)

        # Get image details from EventBridge event
        img_bucket = event["detail"]["bucket"]["name"]
        img_key = event["detail"]["object"]["key"]

        # Extract UUID from filename (assuming filename is UUID.ext or just UUID)
        file_uuid = os.path.splitext(os.path.basename(img_key))[0]
        print(f"Processing file UUID: {file_uuid}")

        print(f"Downloading image: {img_bucket}/{img_key}")
        img_temp_path = f"/tmp/img_{context.aws_request_id}_{os.path.basename(img_key)}"
        s3.download_file(img_bucket, img_key, img_temp_path)

        print("Making predictions...")
        tags = image_prediction(img_temp_path, model_temp_path)

        print(f"Updating DynamoDB for UUID: {file_uuid}")
        # Convert tags before update
        tag_counts = count_items(tags) if tags else {}
        table.update_item(
            Key={"BirdID": file_uuid},
            UpdateExpression="SET tags = :tags",
            ExpressionAttributeValues={":tags": tag_counts},
            ReturnValues="UPDATED_NEW",
        )
        print("DynamoDB updated successfully")

        return {
            "statusCode": 200,
            "body": {
                "message": f"Successfully processed {img_key}",
                "BirdID": file_uuid,
                "tag_counts": tag_counts,
                "bucket": img_bucket,
                "key": img_key,
            },
        }

    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        return {"statusCode": 500, "body": f"Error processing image: {str(e)}"}
