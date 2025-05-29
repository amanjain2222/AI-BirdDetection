import boto3
import cv2
import numpy as np
import os
from io import BytesIO

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Get bucket and object key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Download the image from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    image_data = response['Body'].read()

    # Convert image bytes to numpy array for OpenCV
    np_arr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Resize image to thumbnail (e.g., max 128x128, maintaining aspect ratio)
    thumbnail_size = 128
    h, w = img.shape[:2]
    scale = thumbnail_size / max(h, w)
    new_size = (int(w * scale), int(h * scale))
    thumbnail = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)

    # Encode thumbnail to JPEG with compression
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
    _, buffer = cv2.imencode('.jpg', thumbnail, encode_param)
    thumbnail_bytes = buffer.tobytes()

    # Upload thumbnail to S3 under 'thumbnails/' prefix
    thumb_key = f"thumbnails/{os.path.basename(key)}"
    s3.put_object(Bucket=bucket, Key=thumb_key, Body=thumbnail_bytes, ContentType='image/jpeg')

    return {
        'statusCode': 200,
        'body': f"Thumbnail created and uploaded to {thumb_key}"
    }