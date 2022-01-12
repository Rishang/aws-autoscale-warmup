from utils.event import event_data, ApiGatewayResponse
from ec2 import update_ec2_autoscale
from remove_event import detach_lambda_rule, remove_cloudwatch_rule
from fargate import update_ecs_autoscale

api_return = ApiGatewayResponse()

MIN_COUNT = 1


def lambda_handler(event, handler):
    api_return.body({"response": ""}, status_code=200)

    # get data
    data = event_data(event=event)

    rule_name = data.get("event_rule_name")
    event_statement_id = data.get("statement_id")
    lambda_name = data.get("lambda_function_name")
    autoscaling_group_name = data["autoscaling_group_name"]
    count = int(data["min_count"])
    service_type = data["service_type"]

    # no count be 0
    if count == 0:
        count = MIN_COUNT

    # check for ec2 or ecs
    if service_type.lower() == "ec2":
        scale_response = update_ec2_autoscale(autoscaling_group_name, count)

    elif service_type.lower() in ["ecs", "fargate"]:
        cluster_name = autoscaling_group_name.split("/")[1]
        service_name = autoscaling_group_name.split("/")[2]
        scale_response = update_ecs_autoscale(
            cluster_name=cluster_name, service_name=service_name, min_count=count
        )

    else:
        return False

    # resonse
    removed_event = False

    if scale_response and rule_name != None:
        detach_lambda_rule(function_name=lambda_name, statement_id=event_statement_id)
        removed_event = remove_cloudwatch_rule(name=rule_name)

    api_return.body(
        {"response": {"scaled": scale_response, "event_removed": removed_event}},
        status_code=200,
    )

    return api_return.response()
