import os
import typer
from dotenv import load_dotenv
import boto3
from rich import print


def main():
    typer.confirm("Do you want to create a new instance?", abort=True)
    result = create_ec2_instance()

    print("Here is your EC2 instance:")
    print(result)


def create_ec2_instance():
    load_dotenv(".env")

    REGION = os.getenv('AWS_REGION')
    ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
    SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')

    ec2 = boto3.client(
        'ec2',
        region_name=REGION,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        aws_session_token=SESSION_TOKEN,
    )

    image_id = typer.prompt("What is the Image Id?", default="ami-0b6d6dacf350ebc82")
    subnet_id = typer.prompt("What is the Subnet Id?")
    if subnet_id == "":
        raise typer.BadParameter("Subnet ID is required")
    security_group_id = typer.prompt("What is the Security Group Id?")
    if security_group_id == "":
        raise typer.BadParameter("Security Group ID is required")

    response = ec2.run_instances(
        ImageId=image_id,
        InstanceType="t2.micro",
        MinCount=1,
        MaxCount=1,
        KeyName="vockey",
        NetworkInterfaces=[
            {
                "AssociatePublicIpAddress": True,
                "DeviceIndex": 0,
                "SubnetId": subnet_id,
                "Groups": [security_group_id],
            },
        ],
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": "Webserver"},
                ],
            },
        ],
    )

    return response


if __name__ == '__main__':
    typer.run(main)
