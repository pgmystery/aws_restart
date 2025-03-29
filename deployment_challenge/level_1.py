from components.VPC import VPC
from components.Instance import Instance
from utils import get_public_ip


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
        name="level_1_vpc",
        cidr="10.0.0.0/16",
    )

    try:
        print("CREATE SUBNET...")
        subnet = vpc.create_subnet(
            name="Public Subnet 1",
            cidr="10.0.0.0/24",
            availability_zone="us-west-2a",
        )

        print("CREATE INTERNET-GATEWAY...")
        internet_gateway = vpc.attach_internet_gateway(
            internet_gateway="level_1_ig",
        )

        print("CREATE ROUTE-TABLE...")
        route_table = vpc.create_route_table(
            name="public_route_table_1",
        )
        route_table.associate_subnet(subnet_id=subnet.id)
        route_table.add_route_internet_gateway(
            destination_cidr="0.0.0.0/0",
            internet_gateway_id=internet_gateway.id,
        )

        print("CREATE SECURITY-GROUP...")
        security_group_http = vpc.create_security_group(
            name="level_1_sg_http",
            description="Security Group for VPC 1. (HTTP)"
        )
        security_group_http.add_inbound_rule_cidr(
            protocol="tcp",
            from_port=80,
            to_port=80,
            cidr="0.0.0.0/0",
        )
        security_group_ssh = vpc.create_security_group(
            name="level_1_sg_ssh",
            description="Security Group for VPC 1. (SSH)"
        )
        security_group_ssh.add_inbound_rule_cidr(
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr=f"{get_public_ip()}/32",
        )

        print("CREATE EC2-INSTANCE...")
        instance = Instance(
            name="LAM Server",
            image_id="ami-0f9d441b5d66d5f31",
            availability_zone="us-west-2a",
            instance_type="t2.micro",
            key_pair="vockey",
            subnet_id=subnet.id,
            security_groups=[security_group_http.id, security_group_ssh.id],
            associate_public_ip_address=True,
            user_data=user_data_script
        )

        print(vpc.id)
        print(vpc.name)
        print(instance.id)
    except Exception as error:
        vpc.delete()

        raise error


if __name__ == '__main__':
    main()
