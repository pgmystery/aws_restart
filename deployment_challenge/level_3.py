from threading import Thread

from components.VPC import VPC
from components.NAT import NAT
from components.ElasticIp import ElasticIp
from components.Database import Database, DatabaseEngine
from components.SubnetGroup import SubnetGroup
from components.Instance import Instance
from components.Subnet import Subnet
from user_data_scripts import user_data_lap
from utils import get_public_ip, create_ssh_tunnel


def create_nat_gateway(
    name: str,
    subnet: Subnet,
    allocation: ElasticIp,
    result_dict: dict[str, NAT],
):
    result_dict[name] = NAT(
        name=name,
        subnet=subnet,
        allocation=allocation,
    )


def main():
    print("CREATE VPC...")
    vpc = VPC(
        name="level_3_vpc",
        cidr="10.0.0.0/22"
    )

    print("CREATE SUBNETS...")
    public_subnet_1 = vpc.create_subnet(
        name="level_3_subnet_public_1",
        cidr="10.0.0.0/25",
        availability_zone="us-west-2a",
    )
    public_subnet_2 = vpc.create_subnet(
        name="level_3_subnet_public_2",
        cidr="10.0.0.128/25",
        availability_zone="us-west-2b",
    )
    private_subnet_1 = vpc.create_subnet(
        name="level_3_subnet_private_1",
        cidr="10.0.1.0/24",
        availability_zone="us-west-2a",
    )
    private_subnet_2 = vpc.create_subnet(
        name="level_3_subnet_private_2",
        cidr="10.0.2.0/24",
        availability_zone="us-west-2b",
    )

    print("CREATE INTERNET-GATEWAY...")
    internet_gateway = vpc.attach_internet_gateway(
        internet_gateway="level_3_ig",
    )

    print("CREATE ELASTIC-IP...")
    elastic_ip_1 = ElasticIp(
        name="level_3_elastic_ip_1",
    )
    elastic_ip_2 = ElasticIp(
        name="level_3_elastic_ip_2",
    )

    print("CREATE NATS... (This takes a few minutes)...")

    nats = {}
    t1 = Thread(
        target=create_nat_gateway,
        kwargs={
            "name": "level_3_nat_1",
            "subnet": public_subnet_1,
            "allocation": elastic_ip_1,
            "result_dict": nats,
        }
    )
    t2 = Thread(
        target=create_nat_gateway,
        kwargs={
            "name": "level_3_nat_2",
            "subnet": public_subnet_2,
            "allocation": elastic_ip_2,
            "result_dict": nats,
        }
    )
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    nat_1 = nats["level_3_nat_1"]
    nat_2 = nats["level_3_nat_2"]

    print("CREATE PUBLIC ROUTE-TABLES...")
    route_table_public = vpc.create_route_table(
        name="level_3_route_table_public",
        associate_subnet=[
            public_subnet_1,
            public_subnet_2,
        ]
    )
    route_table_public.add_route_internet_gateway(
        destination_cidr="0.0.0.0/0",
        internet_gateway=internet_gateway,
    )
    route_table_private_1 = vpc.create_route_table(
        name="level_3_route_table_private_1",
        associate_subnet=private_subnet_1
    )
    route_table_private_1.add_route_nat_gateway(
        destination_cidr="0.0.0.0/0",
        nat_gateway=nat_1,
    )
    route_table_private_2 = vpc.create_route_table(
        name="level_3_route_table_private_2",
        associate_subnet=private_subnet_2
    )
    route_table_private_2.add_route_nat_gateway(
        destination_cidr="0.0.0.0/0",
        nat_gateway=nat_2,
    )

    print("CREATE SECURITY GROUPS...")
    security_group_bastion = vpc.create_security_group(
        name="level_3_security_group_bastion",
        description="Level 3 Security Group Bastion (SSH)",
    )
    security_group_bastion.add_inbound_rule_cidr(
        protocol="tcp",
        from_port=22,
        to_port=22,
        cidr=f"{get_public_ip()}/32",
    )

    security_group_web = vpc.create_security_group(
        name="level_3_security_group_web",
        description="Level 3 Security Group WEB (HTTP)",
    )
    security_group_web.add_inbound_rule_sg(
        protocol="tcp",
        from_port=80,
        to_port=80,
        security_group=security_group_bastion,
    )

    security_group_db = vpc.create_security_group(
        name="level_3_security_group_db",
        description="Level 3 Security Group (mysql 3306)",
    )
    security_group_db.add_inbound_rule_sg(
        protocol="tcp",
        from_port=3306,
        to_port=3306,
        security_group=security_group_web,
    )

    print("CREATE DB-SUBNET-GROUP...")
    subnet_group = SubnetGroup(
        name="level_3_subnet_group",
        description="Level 3 Subnet Group",
        subnets=[
            private_subnet_1,
            private_subnet_2,
        ]
    )

    print("CREATE DATABASE... (This takes a few minutes)...")
    database = Database(
        name="level-3-db",  # Needs hyphens
        db_engine=DatabaseEngine.MARIADB,
        db_engine_version="11.4.4",
        master_username="root",
        master_user_password="root1234",
        storage_size_gb=20,
        security_groups=[
            security_group_db,
        ],
        subnet_group=subnet_group,
    )

    print("CREATE 2 BASTION-HOST INSTANCES...")
    bastion_instance_1 = Instance(
        name="Level 3 - Bastion Host 1",
        image_id="ami-0f9d441b5d66d5f31",
        instance_type="t2.micro",
        key_pair="vockey",
        subnet=public_subnet_1,
        security_groups=[security_group_bastion],
        associate_public_ip_address=True,
        availability_zone="us-west-2a",
    )
    bastion_instance_2 = Instance(
        name="Level 3 - Bastion Host 2",
        image_id="ami-0f9d441b5d66d5f31",
        instance_type="t2.micro",
        key_pair="vockey",
        subnet=public_subnet_2,
        security_groups=[security_group_bastion],
        associate_public_ip_address=True,
        availability_zone="us-west-2b",
    )

    print("CREATE 2 WEB-SERVER INSTANCES...")
    web_instance_1 = Instance(
        name="Level 3 - web Server 1",
        image_id="ami-0f9d441b5d66d5f31",
        instance_type="t2.micro",
        key_pair="vockey",
        subnet=private_subnet_1,
        security_groups=[security_group_web],
        associate_public_ip_address=False,
        user_data=user_data_lap.replace("RDS_ENDPOINT_ID", database.endpoint),
        availability_zone="us-west-2a",
    )
    web_instance_2 = Instance(
        name="Level 3 - WEB Server 2",
        image_id="ami-0f9d441b5d66d5f31",
        instance_type="t2.micro",
        key_pair="vockey",
        subnet=private_subnet_2,
        security_groups=[security_group_web],
        associate_public_ip_address=False,
        user_data=user_data_lap.replace("RDS_ENDPOINT_ID", database.endpoint),
        availability_zone="us-west-2b",
    )

    create_ssh_tunnel(
        local_port=8080,
        remote_port=80,
        remote_server_ip=web_instance_1.private_ip,
        ssh_server_ip=bastion_instance_2.public_ip,
    )

    print("DONE!")


if __name__ == '__main__':
    main()
