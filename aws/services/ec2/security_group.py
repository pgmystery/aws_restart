import typer
from rich import print
from rich.table import Table


sg_router = typer.Typer(no_args_is_help=True)


@sg_router.command()
def create(ctx: typer.Context):
    ec2 = ctx.obj["client"]

    vpc_id = typer.prompt("Enter the VPC-Id")
    name = typer.prompt("Enter the Security Group Name")
    description = typer.prompt("Enter the Security Group Description")

    response = ec2.create_security_group(
        VpcId=vpc_id,
        GroupName=name,
        Description=description,
        TagSpecifications=[
            {
                'ResourceType': "security-group",
                "Tags": [
                    {"Key": "Name", "Value": name},
                ],
            },
        ],
    )

    print(response)


@sg_router.command()
def add_rule(ctx: typer.Context):
    ec2 = ctx.obj["client"]

    sg_id = typer.prompt("Enter the Security Group Id")
    protocol = typer.prompt("Enter the Protocol (tcp/udp)", default="tcp")
    cidr = typer.prompt("Enter the Cidr Range")
    from_port = typer.prompt("Enter the From Port")
    to_port = typer.prompt("Enter the To Port")

    response = ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpProtocol=protocol,
        CidrIp=cidr,
        FromPort=from_port,
        ToPort=to_port
    )

    print(response)


@sg_router.command()
def ls(ctx: typer.Context):
    ec2 = ctx.obj["client"]

    response = ec2.describe_security_groups()

    table = Table(title="Security Groups")

    table.add_column("Id")
    table.add_column("Name")
    table.add_column("VPC ID")
    table.add_column("Description")

    for sg in response['SecurityGroups']:
        table.add_row(
            sg["GroupId"],
            sg["GroupName"],
            sg["VpcId"],
            sg["Description"],
        )

    print(table)
