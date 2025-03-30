from deployment_challenge.utils import create_ssh_tunnel
from user_data_scripts import user_data_lam
from utils import get_public_ip

from components.VPC import VPC
from components.Instance import Instance
from components.ElasticIp import ElasticIp
from components.NAT import NAT


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
        subnet=public_subnet,
        allocation=elastic_ip,
    )

    print("CREATE PUBLIC ROUTE-TABLE...")
    route_table_public = vpc.create_route_table(
        name="level_2_route_table_public",
        associate_subnet=public_subnet
    )
    route_table_public.add_route_internet_gateway(
        destination_cidr="0.0.0.0/0",
        internet_gateway=internet_gateway,
    )

    print("CREATE PRIVATE ROUTE-TABLE...")
    route_table_private = vpc.create_route_table(
        name="level_2_route_table_private",
        associate_subnet=private_subnet
    )
    route_table_private.add_route_nat_gateway(
        destination_cidr="0.0.0.0/0",
        nat_gateway=nat,
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
        subnet=public_subnet,
        security_groups=[bastion_security_group],
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
        security_group=bastion_security_group,
    )
    lam_security_group.add_inbound_rule_sg(
        protocol="tcp",
        from_port=80,
        to_port=80,
        security_group=bastion_security_group,
    )

    print("CREATE LAM EC2-INSTANCE...")
    lam_instance = Instance(
        name="Level 2 - LAM Server",
        image_id="ami-0f9d441b5d66d5f31",
        instance_type="t2.micro",
        key_pair="vockey",
        subnet=private_subnet,
        security_groups=[lam_security_group],
        associate_public_ip_address=False,
        user_data=user_data_lam,
        availability_zone="us-west-2a",
    )

    create_ssh_tunnel(
        local_port=8080,
        remote_port=80,
        remote_server_ip=lam_instance.private_ip,
        ssh_server_ip=bastion_instance.public_ip,
    )

    print("DONE!")


if __name__ == '__main__':
    main()
