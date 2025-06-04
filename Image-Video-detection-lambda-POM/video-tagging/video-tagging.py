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


def video_prediction(video_path: str, model_path: str, confidence: int = 0.5):
    """
    Function to make predictions on video frames using a trained YOLO model.

    Parameters:
        video_path (str): Path to the video file.
        model_path (str): path to the model.
        confidence (float): 0-1, only results over this value are saved.
    """
    try:
        # Load video info and extract width, height, and frames per second (fps)
        video_info = sv.VideoInfo.from_video_path(video_path=video_path)
        _, _, fps = int(video_info.width), int(video_info.height), int(video_info.fps)

        model = YOLO(model_path)  # Load your custom-trained YOLO model
        tracker = sv.ByteTrack(frame_rate=fps)  # Initialize the tracker with the video's frame rate
        class_dict = model.names  # Get the class labels from the model

        # Capture the video from the given path
        cap = cv.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Error: couldn't open the video!")

        # Process the video frame by frame
        tags = {}
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:  # End of the video
                break

            # Make predictions on the current frame using the YOLO model
            result = model(frame)[0]
            detections = sv.Detections.from_ultralytics(result)  # Convert model output to Detections format
            detections = tracker.update_with_detections(detections=detections)  # Track detected objects

            # Filter detections based on confidence
            if detections.tracker_id is not None:
                detections = detections[(detections.confidence > confidence)]  # Keep detections with confidence greater than a threashold

                # Generate labels for tracked objects
                labels_1 = [f"{class_dict[cls_id]}" for cls_id, _ in zip(detections.class_id, detections.confidence)]

                update_items(tags, count_items(labels_1))

        return tags

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Release resources
        cap.release()
        print("Video processing complete, Released resources.")


def lambda_handler(event, context):
    model_temp_path = None
    vid_temp_path = None

    try:
        s3 = boto3.client("s3")
        dynamodb = boto3.resource("dynamodb")

        # Get DynamoDB table
        table = dynamodb.Table("BirdStore")

        # Download model
        model_bucket = "birdtagbucket"
        model_key = "models/model.pt"

        print("Downloading model from S3...")
        model_temp_path = f"/tmp/model_{context.aws_request_id}.pt"
        s3.download_file(model_bucket, model_key, model_temp_path)

        # Get video
        vid_bucket = event["Records"][0]["s3"]["bucket"]["name"]
        vid_key = event["Records"][0]["s3"]["object"]["key"]

        # Extract UUID from filename (assuming filename is UUID.ext or just UUID)
        file_uuid = os.path.splitext(os.path.basename(vid_key))[0]
        print(f"Processing file UUID: {file_uuid}")

        print(f"Downloading video: {vid_bucket}/{vid_key}")
        vid_temp_path = f"/tmp/img_{context.aws_request_id}_{os.path.basename(vid_key)}"
        s3.download_file(vid_bucket, vid_key, vid_temp_path)

        print("Making predictions...")
        tags = video_prediction(vid_temp_path, model_temp_path)

        print(f"Updating DynamoDB for UUID: {file_uuid}")
        # Convert tags before update
        tag_counts = tags
        table.update_item(
            Key={"uuid": file_uuid},
            UpdateExpression="SET tags = :tags",
            ExpressionAttributeValues={":tags": count_items(tag_counts)},
            ReturnValues="UPDATED_NEW",
        )
        print("DynamoDB updated successfully")

        return {
            "statusCode": 200,
            "body": {
                "message": f"Successfully processed {vid_key}",
                "uuid": file_uuid,
                "tag_counts": tag_counts,
                "bucket": vid_bucket,
                "key": vid_key,
            },
        }

    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        return {"statusCode": 500, "body": f"Error processing image: {str(e)}"}
