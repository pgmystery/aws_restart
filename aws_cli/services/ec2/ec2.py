import boto3
import typer

from .vpc import vpc_router
from .subnet import subnet_router
from .instance import instance_router
from .security_group import sg_router


ec2_router = typer.Typer(no_args_is_help=True)
ec2_router.add_typer(vpc_router, name="vpc")
ec2_router.add_typer(subnet_router, name="subnet")
ec2_router.add_typer(instance_router, name="instance")
ec2_router.add_typer(sg_router, name="sg")


@ec2_router.callback()
def create_ec2_client(ctx: typer.Context):
    aws_credentials = ctx.obj["credentials"]

    ctx.obj["client"] = boto3.client(
        'ec2',
        region_name=aws_credentials["region"],
        aws_access_key_id=aws_credentials["access_key"],
        aws_secret_access_key=aws_credentials["secret_key"],
        aws_session_token=aws_credentials["session_token"],
    )
