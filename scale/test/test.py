import sys

sys.path.append("../")

from main import lambda_handler

data = {
    "rule_name": "",
    "event_statement_id": "",
    "lambda_name": "",
    "autoscaling_group_name": "scl",
    "min_count": 3,
    "service_type": "ec2",
}

x = lambda_handler(data, "")

print(x)
