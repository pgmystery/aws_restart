import subprocess
from utils import get_public_ip
from pathlib import Path

from components.VPC import VPC
from components.Instance import Instance
from components.ElasticIp import ElasticIp
from components.NAT import NAT


user_data_script = """#!/bin/bash

# Update the system packages
sudo yum update -y

# Install httpd and mariadb (MySQL) server
sudo yum install -y httpd mariadb105-server

# Start the httpd service
sudo systemctl start httpd

# Start the mariadb service
sudo systemctl start mariadb

# Enable the services to start on boot
sudo systemctl enable httpd
sudo systemctl enable mariadb

# Set basic permissions for /var/www directory
sudo chown -R apache:apache /var/www
sudo chmod -R 0770 /var/www
"""


def main():
    print("CREATE VPC...")
    vpc = VPC(
        name="level_2_vpc",
        cidr="10.0.0.0/16",
    )

    print("CREATE PUBLIC SUBNET...")
    public_subnet = vpc.create_subnet(
        name="level_2_public_subnet",
        cidr="10.0.0.0/24",
        availability_zone="us-west-2a",
    )
    print("CREATE PRIVATE SUBNET...")
    private_subnet = vpc.create_subnet(
        name="level_2_private_subnet",
        cidr="10.0.1.0/24",
        availability_zone="us-west-2a",
    )

    print("CREATE INTERNET-GATEWAY...")
    internet_gateway = vpc.attach_internet_gateway(
        internet_gateway="level_2_ig",
    )

    print("CREATE ELASTIC-IP...")
    elastic_ip = ElasticIp(
        name="level_2_elastic_ip",
    )

    print("CREATE NAT... (This takes a few minutes)...")
    nat = NAT(
        name="level_2_nat",
        subnet_id=public_subnet.id,
        allocation_id=elastic_ip.id,
    )

    print("CREATE PUBLIC ROUTE-TABLE...")
    route_table_public = vpc.create_route_table(
        name="level_2_route_table_public",
        associate_subnet=public_subnet.id
    )
    route_table_public.add_route_internet_gateway(
        destination_cidr="0.0.0.0/0",
        internet_gateway_id=internet_gateway.id,
    )

    print("CREATE PRIVATE ROUTE-TABLE...")
    route_table_private = vpc.create_route_table(
        name="level_2_route_table_private",
        associate_subnet=private_subnet.id
    )
    route_table_private.add_route_nat_gateway(
        destination_cidr="0.0.0.0/0",
        nat_gateway_id=nat.id,
    )

    print("CREATE SECURITY-GROUP BASTION-SERVER...")
    bastion_security_group = vpc.create_security_group(
        name="level_2_bastion_security_group",
        description="Level 2 Bastion Security Group",
    )
    bastion_security_group.add_inbound_rule_cidr(
        protocol="tcp",
        from_port=22,
        to_port=22,
        cidr=f"{get_public_ip()}/32",
    )

    print("CREATE BASTION EC2-INSTANCE...")
    bastion_instance = Instance(
        name="Level 2 - Bastion Host",
        image_id="ami-0f9d441b5d66d5f31",
        instance_type="t2.micro",
        key_pair="vockey",
        subnet_id=public_subnet.id,
        security_groups=[bastion_security_group.id],
        associate_public_ip_address=True,
        availability_zone="us-west-2a",
    )

    print("CREATE SECURITY-GROUP LAM-SERVER...")
    lam_security_group = vpc.create_security_group(
        name="level_2_lam_security_group",
        description="Security Group for LEVEL 2 VPC"
    )
    lam_security_group.add_inbound_rule_sg(
        protocol="tcp",
        from_port=22,
        to_port=22,
        sg_id=bastion_security_group.id,
    )
    lam_security_group.add_inbound_rule_sg(
        protocol="tcp",
        from_port=80,
        to_port=80,
        sg_id=bastion_security_group.id,
    )

    print("CREATE LAM EC2-INSTANCE...")
    lam_instance = Instance(
        name="Level 2 - LAM Server",
        image_id="ami-0f9d441b5d66d5f31",
        instance_type="t2.micro",
        key_pair="vockey",
        subnet_id=private_subnet.id,
        security_groups=[lam_security_group.id],
        associate_public_ip_address=False,
        user_data=user_data_script,
        availability_zone="us-west-2a",
    )

    print("SSH TUNNEL TO THE WEBSERVER OVER HTTP")
    while True:
        pem_file_location = input("Enter the PEM file location [./labsuser.pem]: ")
        if pem_file_location == "":
            pem_file_location = "./labsuser.pem"

        pem_file_location = Path(pem_file_location)

        if pem_file_location.is_file():
            break
        else:
            print(f"The PEM file location doesn't exist. ({str(pem_file_location.resolve())})")

    ssh_tunnel_command = [
        "ssh",
        "-oStrictHostKeyChecking=no",
        "-i", pem_file_location.resolve(),
        "-N", "-L", f"localhost:8080:{lam_instance.private_ip}:80",
        f"ec2-user@{bastion_instance.public_ip}"
    ]
    # I can't use .join :(
    ssh_tunnel_command_string = ""
    for word in ssh_tunnel_command:
        ssh_tunnel_command_string += str(word) + " "
    ssh_tunnel_command_string = ssh_tunnel_command_string.strip()
    print(f'RUN COMMAND: "{ssh_tunnel_command_string}"')

    # Run the command in the background using subprocess.Popen
    process = subprocess.Popen(ssh_tunnel_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    print("You can now access the private Web-Server Webpage")
    print(f"URL: http://localhost:8080")
    input("Press enter to exit...")

    try:
        process.terminate()
    except:
        process.kill()

    print("DONE!")


if __name__ == '__main__':
    main()
