import os
import boto3
import logging
import json
import base64
from birdnet_analyzer.analyze.core import analyze
import numba
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute


os.environ["NUMBA_CACHE_DIR"] = "/tmp/numba_cache"
numba.config.CACHE = False

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
AUDIO_DIR = "/tmp/audio"
OUTPUT_DIR = "/tmp/output"

s3 = boto3.client("s3")

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



def download_model_folder():
    MODEL_S3_BUCKET = "birdstore"
    MODEL_S3_PREFIX = "models/V2.4/"
    CHECKPOINT_DIR = "/tmp/checkpoints/V2.4"

    # Skip if already exists
    if os.path.exists(CHECKPOINT_DIR):
        logger.info("✅ Model already downloaded.")
        return

    logger.info("⬇️ Downloading BirdNET model folder...")
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=MODEL_S3_BUCKET, Prefix=MODEL_S3_PREFIX)

    for page in pages:
        for obj in page.get('Contents', []):
            key = obj['Key']
            # Skip 'folders' (empty keys ending with /)
            if key.endswith('/'):
                continue

            rel_path = key[len(MODEL_S3_PREFIX):]
            local_path = os.path.join("/tmp/checkpoints/V2.4", rel_path)

            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            logger.info(f"⬇️ Downloading {key} → {local_path}")
            s3.download_file(MODEL_S3_BUCKET, key, local_path)

    logger.info("✅ Model downloaded to /tmp/checkpoints/V2.4")


def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Credentials": "true"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    try:
        download_model_folder()

        # Parse input
        if not event.get("body"):
            return build_response(400,{
                "message": "No request body found"
            })

        try:
            body = json.loads(event["body"])
        except json.JSONDecodeError:
            return build_response(400, {
                "message": "Invalid JSON in request body"
            })

        if "audio" not in body or "filename" not in body:
            return build_response(400, {
                "message": "Missing 'audio' or 'filename' in request body"
            })

        audio_data = base64.b64decode(body["audio"])
        filename = body["filename"]

        # Save audio to temp file
        os.makedirs(AUDIO_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        local_audio_path = os.path.join(AUDIO_DIR, filename)

        logger.info(f"Saving base64 audio to: {local_audio_path}")
        with open(local_audio_path, "wb") as f:
            f.write(audio_data)

        # Convert to WAV if needed
        input_ext = os.path.splitext(filename)[1].lower()
        if input_ext != ".wav":
            wav_filename = os.path.splitext(filename)[0] + ".wav"
            wav_path = os.path.join(AUDIO_DIR, wav_filename)

            logger.info(f"🎵 Converting {filename} to WAV format...")
            os.system(f"ffmpeg -y -i '{local_audio_path}' -ar 48000 -ac 1 '{wav_path}'")

            logger.info(f"✅ Conversion done: {wav_filename}")
            analysis_input_path = wav_path
        else:
            analysis_input_path = local_audio_path

        # Run BirdNET
        logger.info("🔍 Running BirdNET analysis...")
        species_list = analyze(
            input=analysis_input_path,
            output=OUTPUT_DIR,
        )

        if species_list:
            species_list = species_list[0]  # Unpack nested list
            logger.info(f"📊 Detected species: {species_list}")

            # Query BirdBaseIndex and fetch media for detected species
            matching_media = []
            for species in species_list:
                logger.info(f"🔎 Querying BirdBaseIndex for species: {species}")

                index_entries = BirdBaseIndexModel.query(species.lower())

                for entry in index_entries:
                    logger.info(f"Found MediaID: {entry.MediaID}")
                    # Fetch media info from BirdBase
                    try:
                        media_item = BirdBaseModel.get(entry.MediaID)
                        matching_media.append({
                            "MediaID": media_item.MediaID,
                            "FileType": media_item.FileType,
                            "MediaURL": media_item.MediaURL,
                            "ThumbnailURL": media_item.ThumbnailURL,
                            "Uploader": media_item.Uploader
                        })
                    except BirdBaseModel.DoesNotExist:
                        logger.warning(f"MediaID {entry.MediaID} not found in BirdBase")

            return  build_response(200,{
                "detected_species": species_list,
                "matching_media": matching_media
            })
        else:
            return build_response(200, {
                "detected_species": species_list,
                "matching_media": matching_media
        })

    except Exception as e:
        logger.exception("❌ Lambda error")
        return build_response(500, {"message": str(e)})

