import os
import boto3
import logging
from birdnet_analyzer.analyze.core import analyze
import numba


os.environ["NUMBA_CACHE_DIR"] = "/tmp/numba_cache"
numba.config.CACHE = False

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
AUDIO_DIR = "/tmp/audio"
OUTPUT_DIR = "/tmp/output"

s3 = boto3.client("s3")


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


def lambda_handler(event, context):
    try:
        download_model_folder()

        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        filename = os.path.basename(key)

        dynamodb = boto3.resource("dynamodb")
        table_index = dynamodb.Table("BirdBaseIndex")

        os.makedirs(AUDIO_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        local_audio_path = os.path.join(AUDIO_DIR, filename)
        logger.info(f"⬇️ Downloading audio: s3://{bucket}/{key}")
        s3.download_file(bucket, key, local_audio_path)

        # Convert to .wav if needed
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
            species_list = species_list[0]  # Unpack nested list if needed

            logger.info(f"📊 Detected species: {species_list}")


            bird_id = os.path.splitext(filename)[0]

            # Create BirdBaseIndex entries (one per species)
            for species in species_list:
                table_index.put_item(Item={
                    "TagName": species,
                    "TagValue": 1,
                    "MediaID": bird_id
                })

            return {
                "statusCode": 200,
                "message": f"Stored {len(species_list)} species for {filename}"
            }

    except Exception as e:
        logger.exception("❌ Lambda error")
        return {"statusCode": 500, "error": str(e)}
