from time import sleep

from components.VPC import VPC
from components.Instance import Instance
from components.ElasticIp import ElasticIp
from components.NAT import NAT
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
sudo chmod 2775 /var/www
sudo find /var/www -type d -exec chmod 2775 {} \;
sudo find /var/www -type f -exec chmod 0664 {} \;
"""


def main():
    print("CREATE VPC...")
    vpc = VPC(
        name="level_2_vpc",
        cidr="10.0.0.0/16",
    )

    try:
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

        print("CREATE NAT")
        nat = NAT(
            name="level_2_nat",
            subnet_id=public_subnet.id,
            allocation_id=elastic_ip.id,
        )
        sleep(5)  # Had problem if I don't wait a little

        print("CREATE PUBLIC ROUTE-TABLE...")
        route_table_public = vpc.create_route_table(
            name="level_2_route_table_public",
        )
        route_table_public.associate_subnet(subnet_id=public_subnet.id)
        route_table_public.add_route_internet_gateway(
            destination_cidr="0.0.0.0/0",
            internet_gateway_id=internet_gateway.id,
        )

        print("CREATE PRIVATE ROUTE-TABLE...")
        route_table_private = vpc.create_route_table(
            name="level_2_route_table_private",
        )
        route_table_private.associate_subnet(subnet_id=private_subnet.id)
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
        # TODO:
        lam_security_group.add_inbound_rule_cidr(
            protocol="tcp",
            from_port=80,
            to_port=80,
            cidr="0.0.0.0/0",
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

        print("DONE!")
    except Exception as error:
        vpc.delete()

        raise error


if __name__ == '__main__':
    main()
