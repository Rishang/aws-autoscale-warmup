import json
from bson import json_util
import boto3
import botocore.exceptions
import os

def event_data(event):
    try:
        data = json.loads(event["body"])
    except KeyError:
        data = event
    return data


class ApiGatewayResponse:

    """
    api_response = {
        "statusCode": status_code,
        "body": json.dumps(
            {
                "body": body
            },
            default=json_util.default
        )
    }
    """

    def body(self, data, status_code=200):
        self.BODY = json.dumps({"body": data or ""}, default=json_util.default)
        self.status_code = status_code
        return self.BODY

    def response(self):
        return {
            "statusCode": self.status_code,
            "body": json.dumps({"body": self.BODY}, default=json_util.default),
        }
