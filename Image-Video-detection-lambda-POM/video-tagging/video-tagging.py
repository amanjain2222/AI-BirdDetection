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
                    Item={"TagName": tag_name, "TagValue": tag_value, "MediaID": media_id}
                )
                print(
                    f"Updated tag '{tag_name}' for MediaID '{media_id}' with value {tag_value}"
                )

    except Exception as e:
        print(f"Error in batch writing to DynamoDB: {e}")
        raise


def video_prediction(video_path: str, model_path: str, confidence: int = 0.5, frame_skip: int = 1):
    """
    Function to make predictions on video frames using a trained YOLO model.
    
    Parameters:
        video_path (str): Path to the video file.
        model_path (str): path to the model.
        confidence (float): 0-1, only results over this value are saved.
        frame_skip (int): Process every Nth frame (1 = all frames, 2 = every other frame, etc.)
    """
    try:
        # Load video info and extract width, height, and frames per second (fps)
        video_info = sv.VideoInfo.from_video_path(video_path=video_path)
        _, _, fps = int(video_info.width), int(video_info.height), int(video_info.fps)
        
        # Calculate effective fps after skipping frames
        effective_fps = fps // frame_skip
        print(f"Original FPS: {fps}, Processing every {frame_skip} frames, Effective FPS: {effective_fps}")

        model = YOLO(model_path)  # Load your custom-trained YOLO model
        tracker = sv.ByteTrack(frame_rate=effective_fps)  # Use effective fps for tracker
        class_dict = model.names  # Get the class labels from the model

        # Capture the video from the given path
        cap = cv.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Error: couldn't open the video!")

        # Process the video frame by frame
        tags = {}
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:  # End of the video
                break
            
            # Skip frames based on frame_skip parameter
            if frame_count % frame_skip != 0:
                frame_count += 1
                continue
                
            frame_count += 1

            # Make predictions on the current frame using the YOLO model
            result = model(frame)[0]
            detections = sv.Detections.from_ultralytics(result)
            detections = tracker.update_with_detections(detections=detections)

            # Filter detections based on confidence
            if detections.tracker_id is not None:
                detections = detections[(detections.confidence > confidence)]

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
        # Get environment variables
        table_name = os.environ.get("DYNAMODB_TABLE_NAME", "BirdBaseIndex")
        model_bucket = os.environ.get("MODEL_BUCKET_NAME", "birdstore")
        model_key = os.environ.get("MODEL_KEY", "models/model.pt")
        confidence_threshold = float(os.environ.get("CONFIDENCE_THRESHOLD", "0.5"))
        frame_skip = float(os.environ.get("FRAME_SKIP", "1"))

        print(f"Using DynamoDB table: {table_name}")
        print(f"Using model bucket: {model_bucket}")
        print(f"Using model key: {model_key}")
        print(f"Using confidence threshold: {confidence_threshold}")
        print(f"Using frame skip: {frame_skip}")

        s3 = boto3.client("s3")
        dynamodb = boto3.resource("dynamodb")

        # Get DynamoDB table
        table = dynamodb.Table(table_name)

        # Download model
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
        tags = video_prediction(vid_temp_path, model_temp_path, confidence_threshold, frame_skip)

        print(f"Updating DynamoDB for UUID: {file_uuid}")
        # Convert tags and update DynamoDB
        tag_counts = tags
        if tag_counts:
            update_dynamodb_tags(table, file_uuid, tag_counts)
            print("DynamoDB updated successfully")
        else:
            print("No tags detected, skipping DynamoDB update")

        return {
            "statusCode": 200,
            "body": {
                "message": f"Successfully processed {vid_key}",
                "MediaID": file_uuid,
                "tag_counts": tag_counts,
                "bucket": vid_bucket,
                "key": vid_key,
            },
        }

    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        return {"statusCode": 500, "body": f"Error processing image: {str(e)}"}
