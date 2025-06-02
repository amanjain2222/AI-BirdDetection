from ultralytics import YOLO
import supervision as sv
import cv2 as cv


def count_items(input_list: list):
    """Counts the occurrences of each item in a list and returns a dictionary
    where keys are items and values are their counts.
    """
    counts = {}
    for item in input_list:
        counts[item] = counts.get(item, 0) + 1
    return counts


def update_items(prev_list: dict, curr_list: dict):
    for key, value in curr_list.items():
        # add to dict if key not exist
        if key not in prev_list:
            prev_list[key] = value
        # update to higher value
        else:
            if value > prev_list[key]:
                prev_list[key] = value


def image_prediction(image_path, confidence=0.5, model="./model.pt"):
    """
    Function to make predictions of a pre-trained YOLO model on a given image.

    Parameters:
        image_path (str): Path to the image file. Can be a local path or a URL.
        confidence (float): 0-1, only results over this value are saved.
        model (str): path to the model.
    """
    # Load YOLO model
    model = YOLO(model)
    class_dict = model.names

    # Load image from local path
    img = cv.imread(image_path)

    # Check if image was loaded successfully
    if img is None:
        print("Couldn't load the image! Please check the image path.")
        return

    # Run the model on the image
    result = model(img)[0]

    # Convert YOLO result to Detections format
    detections = sv.Detections.from_ultralytics(result)

    tags = []
    # Filter detections based on confidence threshold and check if any exist
    if detections.class_id is not None:
        detections = detections[(detections.confidence > confidence)]
        
        # Create tags for the detected birds
        tags = [f"{class_dict[cls_id]}" for cls_id, _ in zip(detections.class_id, detections.confidence)]

    return tags


def video_prediction(video_path, confidence=0.5, model="./model.pt"):
    """
    Function to make predictions on video frames using a trained YOLO model.

    Parameters:
        video_path (str): Path to the video file.
        confidence (float): 0-1, only results over this value are saved.
        model (str): path to the model.
    """
    try:
        # Load video info and extract width, height, and frames per second (fps)
        video_info = sv.VideoInfo.from_video_path(video_path=video_path)
        _, _, fps = int(video_info.width), int(video_info.height), int(video_info.fps)

        model = YOLO(model)  # Load your custom-trained YOLO model
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


if __name__ == '__main__':
    print("predicting...")
    tags = image_prediction("./test_images/crows_1.jpg")
    print(tags)

    # uncomment to test video prediction
    # video_prediction("./test_videos/kingfisher.mp4",result_filename='kingfisher_detected.mp4')
    # tags = video_prediction("./test_videos/kingfisher.mp4")
    # print(tags)