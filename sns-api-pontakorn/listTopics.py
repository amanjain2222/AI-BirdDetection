import boto3
import json


def lambda_handler(event, context):
    sns = boto3.client("sns")
    results = sns.list_topics()
    print(f"Retrived topics: {results['Topics']}")

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS, DELETE",
            "Access-Control-Allow-Credentials": "true",
        },
        "body": json.dumps(results["Topics"]),
    }
