import json
from bson import json_util
import boto3


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


class Client:
    def __init__(self):
        pass

    def client(self, client, profile_name=None):
        if profile_name:
            self.profile_name = profile_name
            return boto3.Session(profile_name=profile_name).client(client)
        else:
            return boto3.client(client)
