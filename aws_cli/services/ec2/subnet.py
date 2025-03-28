import typer
from rich import print
from rich.table import Table


subnet_router = typer.Typer(no_args_is_help=True)


@subnet_router.command()
def create(ctx: typer.Context):
    ec2 = ctx.obj["client"]

    vpc_id = typer.prompt("Enter the VPC-ID")
    name = typer.prompt("Enter the Subnet-Name")
    availability_zone = typer.prompt("Enter the Availability Zone (empty for no preference)", default="")
    cidr_block = typer.prompt("Enter the CIDR-Block", default="10.0.0.0/28")

    response = ec2.create_subnet(
        VpcId=vpc_id,
        AvailabilityZone=availability_zone,
        CidrBlock=cidr_block,
        TagSpecifications=[
            {
                'ResourceType': "subnet",
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': name
                    },
                ]
            },
        ],
    )

    print(response)


@subnet_router.command()
def ls(ctx: typer.Context):
    ec2 = ctx.obj["client"]

    response = ec2.describe_subnets()

    table = Table(title="Subnets")

    table.add_column("VPC Id")
    table.add_column("Subnet Id")
    table.add_column("Name")
    table.add_column("Cidr Block")
    table.add_column("Availability Zone")

    for subnet in response['Subnets']:
        subnet_name = ""
        if "Tags" in subnet:
            for tag in subnet['Tags']:
                if tag['Key'] == 'Name':
                    subnet_name = tag['Value']
                    break

        table.add_row(
            subnet['VpcId'],
            subnet['SubnetId'],
            subnet_name,
            subnet["CidrBlock"],
            subnet["AvailabilityZone"],
        )

    print(table)
