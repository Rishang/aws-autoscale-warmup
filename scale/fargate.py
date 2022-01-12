import boto3


def update_ecs_autoscale(service_name, cluster_name, min_count):

    client = boto3.client("application-autoscaling")

    response = client.register_scalable_target(
        ServiceNamespace="ecs",
        ResourceId=f"service/{cluster_name}/{service_name}",
        ScalableDimension="ecs:service:DesiredCount",
        MinCapacity=min_count,
    )

    return response
