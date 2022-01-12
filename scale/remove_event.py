import boto3


def remove_cloudwatch_rule(name):

    client = boto3.client("events")

    list_targets = client.list_targets_by_rule(
        Rule=name,
    )

    ids = []

    for target in list_targets["Targets"]:
        ids.append(target["Id"])

    client.remove_targets(
        Rule=name,
        Ids=ids,
        # Force=True|False
    )

    response = client.delete_rule(Name=name)

    return response


def detach_lambda_rule(function_name, statement_id):
    client = boto3.client("lambda")

    response = client.remove_permission(
        FunctionName=function_name,
        StatementId=statement_id,
    )
    return response
