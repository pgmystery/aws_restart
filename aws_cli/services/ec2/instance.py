import typer
from rich.table import Table


instance_router = typer.Typer(no_args_is_help=True)


@instance_router.command()
def create(ctx: typer.Context):
    ec2 = ctx.obj["client"]

    name = typer.prompt("Enter the instance name")
    image_id = typer.prompt("What is the Image Id?", default="ami-0b6d6dacf350ebc82")
    instance_type = typer.prompt("What instance type?", default="t2.micro")
    key_pair = typer.prompt("Enter the Key-Pair Name", default="vockey")
    subnet_id = typer.prompt("What is the Subnet Id?")
    if subnet_id == "":
        raise typer.BadParameter("Subnet ID is required")
    security_group_id = typer.prompt("What is the Security Group Id?")
    if security_group_id == "":
        raise typer.BadParameter("Security Group ID is required")
    associatePublicIpAddress = typer.confirm("Should the Instance have NO public IP address?", default=False)

    response = ec2.run_instances(
        ImageId=image_id,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        KeyName=key_pair,
        NetworkInterfaces=[
            {
                "AssociatePublicIpAddress": associatePublicIpAddress,
                "DeviceIndex": 0,
                "SubnetId": subnet_id,
                "Groups": [security_group_id],
            },
        ],
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": name},
                ],
            },
        ],
    )

    return response


@instance_router.command()
def ls(ctx: typer.Context):
    ec2 = ctx.obj["client"]

    response = ec2.describe_instances()

    table = Table(title="EC2 Instances")

    table.add_column("Id")
    table.add_column("Name")

    for instance in response['Reservations']:
        instance_name = ""
        if "Tags" in instance:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
                    break

        table.add_row(
            instance["VpcId"],
            instance_name,
        )
