import boto3
import json


def lambda_handler(event, context):
    sns = boto3.client("sns")
    request_body = json.loads(event["body"])
    print(f"Received JSON data: {request_body}")

    topicArn = request_body["topicArn"]
    email = request_body["email"]

    try:
        subscription = sns.subscribe(
            TopicArn=topicArn, Protocol="email", Endpoint=email
        )
    except Exception as e:
        print(f"Error subscribing email {email} to topic {topicArn}: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps("Error subscribing email to topic"),
        }
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS, DELETE",
            "Access-Control-Allow-Credentials": "true",
        },
        "body": json.dumps(
            {
                "success": True,
                "message": f"Email {email} subscribed to topic successfully",
                "topicArn": topicArn,
                "subscriptionArn": subscription.get("SubscriptionArn"),
                "email": email,
            }
        ),
    }
