# SNS Lambda Functions

Two AWS Lambda functions for managing Amazon SNS topics and subscriptions.

## Functions

### listTopics.py
**Purpose**: Retrieves all available SNS topics

**Method**: GET  
**Response**: JSON array of SNS topics with their ARNs

### subscribeTopic.py  
**Purpose**: Subscribes an email address to an SNS topic

**Method**: POST  
**Request Body**:
```json
{
  "topicArn": "arn:aws:sns:region:account:topic-name",
  "email": "user@example.com"
}
```

**Response**: Subscription confirmation with subscription ARN

## CORS Configuration
Both functions are configured for local development with:
- Origin: `http://localhost:3000`
- Methods: GET, POST, OPTIONS
- Credentials: Enabled

## IAM Permissions Required
- `sns:ListTopics` (for listTopics)
- `sns:Subscribe` (for subscribeTopic)

## Error Handling
- subscribeTopic includes try/catch with 500 status code for subscription failures
- Both functions include request logging for debugging