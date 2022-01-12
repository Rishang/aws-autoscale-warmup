import boto3
from datetime import datetime, date
import json


def time(datetime_str):
    return datetime.strptime(datetime_str, "%d/%m/%Y %H:%M:%S")


def datetime_to_cron(dt):
    # FYI: not all cron implementations
    return f"cron({dt.minute} {dt.hour} {dt.day} {dt.month} ? {dt.year})"


def attach_event_rule(lambda_arn, event_arn, statement_id: str):

    client = boto3.client("lambda")

    trigger = client.add_permission(
        FunctionName=lambda_arn.split(":")[-1],
        StatementId=statement_id,
        Action="lambda:InvokeFunction",
        Principal="events.amazonaws.com",
        SourceArn=event_arn,
    )
    return trigger


def put_rule(name, time, input_data, lambda_arn):

    client = boto3.client("events")

    rule = client.put_rule(
        Name=name,
        ScheduleExpression=datetime_to_cron(time),
        State="ENABLED",
        Description="event to auto-scale",
        # RoleArn=''
    )

    rule_targets = client.put_targets(
        Rule=name,
        Targets=[
            {
                # a uniq id
                "Id": rule["ResponseMetadata"]["RequestId"],
                "Arn": lambda_arn,
                "Input": json.dumps(input_data),
            },
        ],
    )
    return {"rule": rule, "rule_targets": rule_targets}
