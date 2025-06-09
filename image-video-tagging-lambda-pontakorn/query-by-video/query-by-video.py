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
        raise

    finally:
        # Release resources
        if cap:
            cap.release()
            print("Released video capture resources.")


def lambda_handler(event, context):
    model_temp_path = None
    vid_temp_path = None

    try:
        # Get environment variables
        model_bucket = os.environ.get("MODEL_BUCKET_NAME", "birdstore")
        model_key = os.environ.get("MODEL_KEY", "models/model.pt")
        confidence_threshold = float(os.environ.get("CONFIDENCE_THRESHOLD", "0.5"))
        frame_skip = int(os.environ.get("FRAME_SKIP", "1"))

        print(f"Using model bucket: {model_bucket}")
        print(f"Using model key: {model_key}")
        print(f"Using confidence threshold: {confidence_threshold}")
        print(f"Using frame skip: {frame_skip}")

        s3 = boto3.client("s3")

        # Download model
        print("Downloading model from S3...")
        model_temp_path = f"/tmp/model_{context.aws_request_id}_{os.path.basename(model_key)}"
        s3.download_file(model_bucket, model_key, model_temp_path)

        # Process base64 encoded video from request
        if not event.get("body"):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No request body found"}),
            }

        # Parse JSON body to get base64 video data
        try:
            body = json.loads(event["body"])
        except json.JSONDecodeError:
            return _.build_response(400, {
                "message": "An error occurred while processing your request",
                "error": "Invalid JSON in request body"
            })

        # Extract base64 video data
        if "video" not in body:
            return _.build_response(400, {
                "message": "An error occurred while processing your request",
                "error": "No 'image' field found in request body"
            })

        print("Processing base64 encoded video data...")
        try:
            video_data = base64.b64decode(body["video"])
        except Exception as e:
            return _.build_response(400, {
                "message": "An error occurred while processing your request",
                "error": f"Invalid base64 image data: {str(e)}"
            })

        # Save video data to temporary file
        print("Saving video data to temporary file...")

        vid_temp_path = f"/tmp/img_{context.aws_request_id}"

        with open(vid_temp_path, "wb") as f:
            f.write(video_data)

        print("Making predictions...")
        try:
            tags = video_prediction(vid_temp_path, model_temp_path, confidence_threshold, frame_skip)
        except Exception as e:
            return _.build_response(500, {
                "message": "An error occurred while processing your request",
                "error": f"Video processing failed: {str(e)}"
            })

        # Convert tags
        filter_tags = tags if tags else {}
        
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
