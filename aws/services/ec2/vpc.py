import typer
from rich import print
from rich.table import Table


vpc_router = typer.Typer(no_args_is_help=True)


@vpc_router.command()
def create(ctx: typer.Context):
    ec2 = ctx.obj["client"]

    vpc_name = typer.prompt("Enter the VPC-Name")
    ipv4_cidr = typer.prompt("Enter the IPv4-CIDR Block", default="10.0.0.0/24")

    response = ec2.create_vpc(
        CidrBlock=ipv4_cidr,
        InstanceTenancy='default',
        TagSpecifications=[
            {
                'ResourceType': 'vpc',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': vpc_name,
                    },
                ]
            },
        ],
    )

    print(response)


@vpc_router.command()
def ls(ctx: typer.Context):
    ec2 = ctx.obj["client"]

    response = ec2.describe_vpcs()

    table = Table(title="VPCs")

    table.add_column("Id")
    table.add_column("Name")
    table.add_column("CIDR-Block")

    for vpc in response['Vpcs']:
        vpc_name = ""
        if "Tags" in vpc:
            for tag in vpc['Tags']:
                if tag['Key'] == 'Name':
                    vpc_name = tag['Value']
                    break

        table.add_row(
            vpc["VpcId"],
            vpc_name,
            vpc["CidrBlock"],
        )

    print(table)
