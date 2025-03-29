from typing import Optional, Union, Any

from .AWS import EC2
from .InternetGateway import InternetGateway
from .SecurityGroup import SecurityGroup
from .Subnet import Subnet
from .RouteTable import RouteTable


class VPC(EC2):
    def __init__(self, name: str, cidr: str, **kwargs):
        super().__init__()

        self.internet_gateway: Optional[InternetGateway] = None
        self.subnets: list[Subnet] = []
        self.route_tables: list[RouteTable] = []

        tags = kwargs["Tags"] if "Tags" in kwargs else []

        self.name: str = name
        self.cidr_block: str = cidr
        self.info: dict[str, Any] = self.client.create_vpc(
            InstanceTenancy='default',
            **kwargs,
            CidrBlock=cidr,
            TagSpecifications=[
                {
                    'ResourceType': 'vpc',
                    'Tags': [
                        *tags,
                        {
                            'Key': 'Name',
                            'Value': name,
                        },
                    ]
                },
            ],
        )["Vpc"]
        self.id: str = self.info["VpcId"]

    def delete(self):
        return self.client.delete_vpc(
            VpcId=self.id,
        )

    def create_subnet(self, name: str, cidr: str, availability_zone: str = "", **kwargs) -> Subnet:
        subnet = Subnet(name, self, cidr, availability_zone, **kwargs)
        self.subnets.append(subnet)

        return subnet

    def attach_internet_gateway(self, internet_gateway: Union[InternetGateway,  str]) -> InternetGateway:
        if type(internet_gateway) == str:
            internet_gateway = InternetGateway(internet_gateway)

        self.internet_gateway = internet_gateway

        self.client.attach_internet_gateway(
            InternetGatewayId=internet_gateway.id,
            VpcId=self.id,
        )

        return internet_gateway

    def create_route_table(self, name: str, associate_subnet: Subnet = None, **kwargs) -> RouteTable:
        route_table = RouteTable(name, self, **kwargs)
        self.route_tables.append(route_table)

        if associate_subnet is not None:
            route_table.associate_subnet(associate_subnet)

        return route_table

    def create_security_group(self, name: str, description: str, **kwargs) -> SecurityGroup:
        return SecurityGroup(name, description, self, **kwargs)
