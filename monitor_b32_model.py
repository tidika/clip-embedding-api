import boto3

region = "us-east-1"
endpoint_name = "clip-vit-b32"
sns_topic_name = "ClipB32ModelAlarm"

cloudwatch = boto3.client("cloudwatch", region_name=region)
sns = boto3.client("sns", region_name=region)

# Get the ARN for the SNS topic
response = sns.list_topics()
topic_arn = next(
    (t["TopicArn"] for t in response["Topics"] if t["TopicArn"].endswith(sns_topic_name)),
    None
)

if topic_arn is None:
    raise Exception(f"SNS topic '{sns_topic_name}' not found.")

alarms = [
    {
        "name": f"{endpoint_name}-HighMemoryUtilization",
        "metric": "MemoryUtilization",
        "threshold": 70.0,
        "comparison": "GreaterThanThreshold",
        "stat": "Average",
        "unit": "Percent"
    },
    {
        "name": f"{endpoint_name}-HighModelLatency",
        "metric": "ModelLatency",
        "threshold": 15000.0,
        "comparison": "GreaterThanThreshold",
        "stat": "Average",
        "unit": "Milliseconds"
    },
    {
        "name": f"{endpoint_name}-High4XXErrors",
        "metric": "4XX",
        "threshold": 2.0,
        "comparison": "GreaterThanThreshold",
        "stat": "Sum",
        "unit": "Count"
    },
    {
        "name": f"{endpoint_name}-High5XXErrors",
        "metric": "5XX",
        "threshold": 2.0,
        "comparison": "GreaterThanThreshold",
        "stat": "Sum",
        "unit": "Count"
    },
    {
        "name": f"{endpoint_name}-HighInvocationCount",
        "metric": "InvocationCount",
        "threshold": 50.0,
        "comparison": "GreaterThanThreshold",
        "stat": "Sum",
        "unit": "Count",
        "period": 300  # 5 minutes
    },
    {
        "name": f"{endpoint_name}-ThrottledInvocations",
        "metric": "ThrottledInvocations",
        "threshold": 1.0,
        "comparison": "GreaterThanThreshold",
        "stat": "Sum",
        "unit": "Count"
    }
]

for alarm in alarms:
    cloudwatch.put_metric_alarm(
        AlarmName=alarm["name"],
        MetricName=alarm["metric"],
        Namespace="AWS/SageMaker",
        Dimensions=[
            {
                "Name": "EndpointName",
                "Value": endpoint_name
            }
        ],
        Period=60,
        EvaluationPeriods=1,
        Threshold=alarm["threshold"],
        ComparisonOperator=alarm["comparison"],
        Statistic=alarm["stat"],
        Unit=alarm["unit"],
        AlarmDescription=f"Alarm for {alarm['metric']} on {endpoint_name}",
        ActionsEnabled=True,
        AlarmActions=[topic_arn]
    )

print("Alarms with SNS notifications created successfully.")
