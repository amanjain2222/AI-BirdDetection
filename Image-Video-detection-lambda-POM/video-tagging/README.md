# Video Tagging Lambda Function

A serverless AWS Lambda function that automatically tags videos using a pre-trained YOLO model. This function is triggered by S3 events, processes uploaded videos to detect objects, and stores the results in DynamoDB.

## Overview

This Lambda function performs the following operations:
1. Downloads a YOLO model from S3
2. Processes videos uploaded to an S3 bucket
3. Runs object detection using the YOLO model
4. Stores detected object tags and counts in DynamoDB

## Architecture

```
S3 Bucket (videos) → Lambda Function → DynamoDB Table
     ↑                      ↓
S3 Bucket (Model) ←─────────┘
```

## Features

- **Automatic Processing**: Triggered by S3 upload events
- **Object Detection**: Uses YOLO (You Only Look Once) for real-time object detection
- **Configurable Confidence**: Adjustable confidence threshold for detections
- **Tag Counting**: Counts occurrences of each detected object
- **Environment Variable Configuration**: Flexible configuration via environment variables
- **Error Handling**: Comprehensive error handling and logging

## Prerequisites

- AWS Account with appropriate permissions
- S3 buckets for storing videos and the YOLO model
- DynamoDB table for storing results
- Docker for building the Lambda container image

## Environment Variables

| Variable Name | Description | Default Value | Required |
|---------------|-------------|---------------|----------|
| `DYNAMODB_TABLE_NAME` | Name of the DynamoDB table to store results | `BirdBase` | No |
| `MODEL_BUCKET_NAME` | S3 bucket containing the YOLO model | `birdstore` | No |
| `MODEL_KEY` | S3 key path to the YOLO model file | `models/model.pt` | No |
| `CONFIDENCE_THRESHOLD` | Confidence threshold for prediction | `0.5` | No |
| `FRAME_SKIP` | Process every Nth frame for prediction | `1` | No |

## DynamoDB Table Schema

The function expects a DynamoDB table with the following structure:

| Attribute | Type | Description |
|-----------|------|-------------|
| `MediaID` | String (Primary Key) | UUID extracted from the video filename |
| `tags` | Map | Dictionary of detected objects and their counts |

## Deployment

### 1. Build the Docker Image

```bash
docker build -t video-tagging-lambda .
```

### 2. Tag and Push to ECR

```bash
# Create ECR repository (if not exists)
aws ecr create-repository --repository-name video-tagging-lambda

# Get login token
aws ecr get-login-password --region <your-region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<your-region>.amazonaws.com

# Tag and push
docker tag video-tagging-lambda:latest <account-id>.dkr.ecr.<your-region>.amazonaws.com/video-tagging-lambda:latest
docker push <account-id>.dkr.ecr.<your-region>.amazonaws.com/video-tagging-lambda:latest
```

### 3. Create Lambda Function

```bash
aws lambda create-function \
  --function-name video-tagging-lambda \
  --package-type Image \
  --code ImageUri=<account-id>.dkr.ecr.<your-region>.amazonaws.com/video-tagging-lambda:latest \
  --role arn:aws:iam::<account-id>:role/lambda-execution-role \
  --environment Variables='{
    "DYNAMODB_TABLE_NAME":"YourTableName",
    "MODEL_BUCKET_NAME":"your-model-bucket",
    "MODEL_KEY":"path/to/your/model.pt"
  }'
```

## AWS Resources

### Recommended Lambda Configuration

| Setting | Recommended Value | Notes |
|---------|------------------|-------|
| **Memory** | 4096 MB | Required for YOLO model processing |
| **Timeout** | 15 minutes (900 seconds) | Allow time for model download and inference |
| **Ephemeral Storage** | 2048 MB | Temporary storage for model and video files |
| **Architecture** | x86_64 | Required for OpenCV and YOLO dependencies |

### IAM Permissions

The Lambda execution role requires the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::your-video-bucket/*",
        "arn:aws:s3:::your-model-bucket/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:UpdateItem"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/YourTableName"
    }
  ]
}
```

### S3 Event Configuration

Configure S3 to trigger the Lambda function on object creation:

```json
{
  "Rules": [
    {
      "Name": "VideoUploadTrigger",
      "Status": "Enabled",
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "suffix",
              "Value": ".mp4"
            }
          ]
        }
      },
      "Configuration": {
        "LambdaConfiguration": {
          "LambdaFunctionArn": "arn:aws:lambda:region:account:function:video-tagging-lambda",
          "Events": ["s3:ObjectCreated:*"]
        }
      }
    }
  ]
}
```

## Dependencies

The function uses the following Python packages (see `requirements.txt`):

- `boto3` - AWS SDK for Python
- `opencv-python-headless` - Computer vision library
- `ultralytics` - YOLO implementation
- `supervision` - Computer vision utilities
- `torch` - PyTorch deep learning framework

## Usage

1. Upload your trained YOLO model to the specified S3 bucket
2. Configure the Lambda function with appropriate environment variables
3. Set up S3 event notifications to trigger the function
4. Upload videos to the monitored S3 bucket
5. Check DynamoDB for the tagged results

## Input Format

The function expects S3 events in the standard format:

```json
{
  "Records": [
    {
      "s3": {
        "bucket": {
          "name": "your-video-bucket"
        },
        "object": {
          "key": "uuid-filename.mp4"
        }
      }
    }
  ]
}
```

## Output Format

The function returns a response with the following structure:

```json
{
  "statusCode": 200,
  "body": {
    "message": "Successfully processed video.mp4",
    "MediaID": "uuid-from-filename",
    "tag_counts": {
      "bird": 2,
      "tree": 1
    },
    "bucket": "your-video-bucket",
    "key": "uuid-filename.mp4"
  }
}
```

## Monitoring and Troubleshooting

### CloudWatch Logs

Monitor the function execution through CloudWatch Logs. Key log messages include:
- Model download progress
- Video processing status
- DynamoDB update confirmations
- Error messages and stack traces

### Common Issues

1. **Memory Issues**: Increase Lambda memory allocation if encountering OOM errors
2. **Timeout**: Extend timeout duration for large videos or slow model inference
3. **Permissions**: Ensure IAM role has all required permissions
4. **Model Path**: Verify the YOLO model exists at the specified S3 location

### Performance Optimization

- **Container Reuse**: Lambda containers are reused, so model downloads are cached
- **Video Preprocessing**: Consider resizing large videos before processing
- **Batch Processing**: For high-volume scenarios, consider batch processing multiple videos

## Cost Considerations

- **Compute Costs**: Based on memory allocation and execution time
- **Storage Costs**: Ephemeral storage for temporary files
- **Data Transfer**: S3 download costs for model and videos
- **DynamoDB**: Write capacity units for storing results

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.