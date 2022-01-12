import boto3
from botocore.exceptions import ClientError
import os
import json
from datetime import datetime
import time
import uuid
import shedule_table as st
from utils.event import event_data, ApiGatewayResponse
from shedule_event import datetime_to_cron, put_rule, attach_event_rule
import yaml

api_return = ApiGatewayResponse()


def get_s3_file(bucket_name, file_name):

    print(f"bucket: {bucket_name} / {file_name}")
    s3 = boto3.resource("s3")

    file = s3.Object(bucket_name, file_name)
    
    shed = file.get()["Body"].read()

    # check for json or yml
    __file_ext = file_name.split(".")[-1:][0]

    if __file_ext == "json":
        data: dict = json.loads(shed)
    elif __file_ext in ["yml","yaml"]:
        data: dict = yaml.full_load(shed)
    else:
        print(f"File ext: {__file_ext}")
        raise Exception("not json or yaml")
    return data

def generate_rules(event):

    print("current time:")
    print(datetime.now().time())

    print("current timezone")
    print(time.tzname)

    # cloud watch event rule
    event_rule_prefix = os.environ.get("EVENT_RULE_PREFIX") or "event-scale"

    # next lambda
    lambda_arn = os.environ.get("AUTOSCALE_LAMBDA_ARN")

    lambda_name = lambda_arn.split(":")[-1] if isinstance(lambda_arn, str) else ""

    # extra info
    aws_region = lambda_arn.split(":")[3] if isinstance(lambda_arn, str) else ""
    account_id = lambda_arn.split(":")[4] if isinstance(lambda_arn, str) else ""

    # main
    data = event_data(event=event)

    shedule_time = data["shedule_table"]
    # scaling target
    autoscaling_group_name = data["scaling_group_name"]
    service_type = data["service_type"]

    df = st.get_shedule(shedule_time)

    tf, end_time = st.shedule(df)

    api_return.body({"response": ""}, status_code=200)

    for index, row in tf.iterrows():

        utc_time = row["utc_time"]
        min_count = row["count"]

        print("utc_time: " + datetime_to_cron(utc_time))
        print("time: " + datetime_to_cron(row["time"]))
        print(min_count)
        # print(index)

        rule_name = f"{event_rule_prefix}-{uuid.uuid4()}"
        statement_id = f"id-{rule_name}"

        r = put_rule(
            name=rule_name,
            time=utc_time,
            input_data={
                "min_count": min_count,
                "autoscaling_group_name": autoscaling_group_name,
                "service_type": service_type,
                "event_rule_arn": f"arn:aws:events:{aws_region}:{account_id}:rule/{event_rule_prefix}-{index}",
                "event_rule_name": rule_name,
                "statement_id": statement_id,
                "lambda_function_name": lambda_name,
            },
            lambda_arn=lambda_arn,
        )

        if r:
            a = attach_event_rule(
                lambda_arn=lambda_arn,
                event_arn=r["rule"]["RuleArn"],
                statement_id=statement_id,
            )

    api_return.body({"response": {"rule": r, "lambda": a}}, status_code=200)

    return api_return.response()


def multi_sevice_shedule_rule(event, handler):

    if not isinstance(event, list):
        bucket_name = os.environ.get("BUCKET_NAME")
        bucket_file = os.environ.get("BUCKET_FILE")
        event = get_s3_file(bucket_name, bucket_file)

    resoponses = []
    for every in event:
        if not isinstance(every["shedule_table"], dict):
            assert "invalid input"

        resoponses.append(generate_rules(every))

    return resoponses
