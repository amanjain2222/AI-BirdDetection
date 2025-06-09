import boto3
import cv2 as cv
import os
import json
import supervision as sv
from ultralytics import YOLO


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


def generate_presigned_url(s3_client, bucket: str, key: str, expiration: int = 3600):
    """
    Generate a presigned URL for an S3 object.

    Parameters:
        s3_client: Boto3 S3 client
        bucket (str): S3 bucket name
        key (str): S3 object key
        expiration (int): URL expiration time in seconds (default: 1 hour)

    Returns:
        str: Presigned URL or None if error
    """
    try:
        response = s3_client.generate_presigned_url(
            "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=expiration
        )
        return response
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None


def publish_sns_notification(sns_client, tag_name: str, message_data: dict):
    """
    Publish a notification to SNS topic based on tag name.
    Creates the topic if it doesn't exist.

    Parameters:
        sns_client: Boto3 SNS client
        tag_name (str): The tag name (used as topic name)
        message_data (dict): Data to include in the message
    """
    try:
        # Sanitize tag name for SNS topic naming
        sanitized_tag_name = tag_name.replace(" ", "-").replace("_", "-").lower()

        # Create or get existing topic (CreateTopic is idempotent)
        response = sns_client.create_topic(Name=sanitized_tag_name)
        topic_arn = response["TopicArn"]
        print(f"Using SNS topic: {topic_arn}")

        # Prepare the message
        message = {
            "url": message_data.get("media_url"),
            "timestamp": message_data.get("timestamp"),
        }

        # Publish to SNS
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=json.dumps(message),
            Subject=f"Someone just uploaded a new {tag_name} media!",
        )

        print(
            f"Successfully published SNS notification for tag '{tag_name}' to {topic_arn}"
        )
        return response["MessageId"]

    except Exception as e:
        print(f"Error publishing SNS notification for tag '{tag_name}': {e}")
        return None


def update_dynamodb_tags(table, media_id: str, tag_counts: dict):
    """
    Creates separate items for each tag with TagName as hash key and MediaID as range key.
    Overwrites existing items without checking.

    Parameters:
        table: DynamoDB table resource
        media_id (str): The media ID to associate with tags
        tag_counts (dict): Dictionary of tag names and their counts
    """
    try:
        # Use batch writing for better performance
        with table.batch_writer() as batch:
            for tag_name, tag_value in tag_counts.items():
                batch.put_item(
                    Item={
                        "TagName": tag_name,
                        "TagValue": tag_value,
                        "MediaID": media_id,
                    }
                )
                print(
                    f"Updated tag '{tag_name}' for MediaID '{media_id}' with value {tag_value}"
                )

    except Exception as e:
        print(f"Error in batch writing to DynamoDB: {e}")
        raise


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
        confidence_threshold = float(os.environ.get("CONFIDENCE_THRESHOLD", "0.5"))
        presigned_url_expiration = int(
            os.environ.get("PRESIGNED_URL_EXPIRATION", "86400") # 24 hours default
        ) 

        print(f"Using DynamoDB table: {table_name}")
        print(f"Using model bucket: {model_bucket}")
        print(f"Using model key: {model_key}")
        print(f"Using confidence threshold: {confidence_threshold}")
        print(f"Using presigned url expiration: {presigned_url_expiration}")

        s3 = boto3.client("s3")
        dynamodb = boto3.resource("dynamodb")
        sns = boto3.client("sns")

        # Get DynamoDB table
        table = dynamodb.Table(table_name)

        # Download model
        print("Downloading model from S3...")
        model_temp_path = (
            f"/tmp/model_{context.aws_request_id}_{os.path.basename(model_key)}"
        )
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
        tags = image_prediction(img_temp_path, model_temp_path, confidence_threshold)

        print(f"Updating DynamoDB for UUID: {file_uuid}")
        # Convert tags and update DynamoDB
        tag_counts = count_items(tags) if tags else {}

        if tag_counts:
            update_dynamodb_tags(table, file_uuid, tag_counts)
            print("DynamoDB updated successfully")

            # Generate presigned URL for the image
            presigned_url = generate_presigned_url(
                s3, img_bucket, img_key, presigned_url_expiration
            )

            if presigned_url:
                print("Generated presigned URL for image")

                # Publish SNS notifications for each detected tag
                from datetime import datetime, timezone

                current_timestamp = datetime.now(timezone.utc).isoformat() + "Z"

                sns_message_ids = []
                for tag_name, tag_count in tag_counts.items():
                    message_data = {
                        "media_id": file_uuid,
                        "tag_count": tag_count,
                        "media_url": presigned_url,
                        "bucket": img_bucket,
                        "key": img_key,
                        "timestamp": current_timestamp,
                    }

                    message_id = publish_sns_notification(sns, tag_name, message_data)
                    if message_id:
                        sns_message_ids.append(
                            {"tag": tag_name, "message_id": message_id}
                        )

                print(f"Published {len(sns_message_ids)} SNS notifications")
            else:
                print("Failed to generate presigned URL, skipping SNS notifications")
                sns_message_ids = []
        else:
            print("No tags detected, skipping DynamoDB update and SNS notifications")
            sns_message_ids = []

        return {
            "statusCode": 200,
            "body": {
                "message": f"Successfully processed {img_key}",
                "MediaID": file_uuid,
                "tag_counts": tag_counts,
                "bucket": img_bucket,
                "key": img_key,
                "sns_notifications": sns_message_ids,
                "presigned_url_generated": presigned_url is not None,
            },
        }

    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        return {"statusCode": 500, "body": f"Error processing image: {str(e)}"}

    finally:
        # Clean up temporary files
        for temp_path in [model_temp_path, img_temp_path]:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                    print(f"Cleaned up temporary file: {temp_path}")
                except Exception as e:
                    print(f"Warning: Could not clean up {temp_path}: {e}")
