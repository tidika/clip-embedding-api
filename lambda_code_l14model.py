import json
import boto3
import base64
import numpy as np

runtime = boto3.client("sagemaker-runtime", region_name="us-east-1")


def lambda_handler(event, context):
    try:
        # If coming from API Gateway with stringified JSON
        if isinstance(event, str):
            event = json.loads(event)
        elif "body" in event:  # API Gateway proxy integration
            body = event["body"]
            if isinstance(body, str):
                event = json.loads(body)
            else:
                event = body

        # Build payload depending on input type
        if "text" in event:
            payload = {"inputs": {"text": event["text"]}}
        elif "image" in event:
            payload = {"inputs": {"image": event["image"]}}
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'text' or 'image' key in input"}),
                "headers": {"Content-Type": "application/json"},
            }

        # Call the SageMaker endpoint
        response = runtime.invoke_endpoint(
            EndpointName="l14-clip-model-v1",
            ContentType="application/json",
            Body=json.dumps(payload),
        )

        # Read and return the response from SageMaker
        result = json.loads(response["Body"].read().decode())

        if isinstance(result, list):
            result = np.array(result)
            norm = np.linalg.norm(result)
        if norm > 0:
            result = (result / norm).tolist() #performs normalization on the returned embedding
        else:
            result = result.tolist()

        return {
            "statusCode": 200,
            "body": json.dumps(result),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        }
