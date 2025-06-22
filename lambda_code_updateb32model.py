import boto3

sm_client = boto3.client("sagemaker", region_name="us-east-1")

def lambda_handler(event, context):


    endpoint_name = event["endpoint_name"]
    endpoint_config_name = event["endpoint_config_name"]

    try:
        # Check if the endpoint exists
        sm_client.describe_endpoint(EndpointName=endpoint_name)

        # If it exists, update it
        response = sm_client.update_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=endpoint_config_name
        )
        return {
            "statusCode": 200,
            "body": f"Updated Endpoint: {response['EndpointArn']}"
        }

    except sm_client.exceptions.ClientError as e:
        if "Could not find endpoint" in str(e):
            # Create the endpoint if it doesn't exist
            response = sm_client.create_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=endpoint_config_name
            )
            return {
                "statusCode": 200,
                "body": f"Created Endpoint: {response['EndpointArn']}"
            }
        else:
            raise e
