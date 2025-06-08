import boto3
import json
from urllib.parse import urlparse

s3_client = boto3.client('s3')

def clean_url(url):
    try:
        url = url.strip()
        return url
    except Exception as e:
        print(f"Error cleaning URL: {e}")
        return ""

def extract_s3_url(presigned_url):
    try:
        print(f"Extracting S3 URL from presigned URL: {presigned_url}")
        parsed = urlparse(presigned_url)
        s3_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        return s3_url
    except Exception as e:
        print(f"Error extracting S3 URL: {e}")
        return ""

def parse_s3_url(s3_url):    
    try:
        parsed = urlparse(s3_url)
        bucket = parsed.netloc.split('.')[0]
        key = parsed.path.lstrip('/')
        return bucket, key
    except Exception as e:
        print(f"Error parsing S3 URL: {e}")
        return None

# Helper function: generate a pre-signed URL
def generate_presigned_url(s3_url, s3_client = boto3.client('s3'), expiration=3600):
    try: 
        bucket, key = parse_s3_url(s3_url)
        return s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=expiration
        )
    except Exception as e:
        return ""

def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS, DELETE",
            "Access-Control-Allow-Credentials": "true"
        },
        "body": json.dumps(body)
    }

if __name__ == "__main__":
    s3_url = "https://dummy-bucket.s3.amazonaws.com/media/sample.jpg"
    presigned_url = generate_presigned_url(s3_url, s3_client)
    print(f"Presigned URL: {presigned_url}")

    s3_url = extract_s3_url(presigned_url)
    print(f"Extracted S3 URL: {s3_url}")

    s3_url = ""
    presigned_url = generate_presigned_url(s3_url, s3_client)
    print(f"Presigned URL: {presigned_url}")

    
