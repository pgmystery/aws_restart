from .AWS import EC2
from .InternetGateway import InternetGateway
from .SecurityGroup import SecurityGroup
from .Subnet import Subnet
from .RouteTable import RouteTable


class VPC(EC2):
    def __init__(self, name: str, cidr: str, **kwargs):
        super().__init__()

        self.internet_gateway = None
        self.subnets = []
        self.route_tables = []

        tags = kwargs["Tags"] if "Tags" in kwargs else []

        self.name = name
        self.cidr_block = cidr
        self.info = self.client.create_vpc(
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
        self.id = self.info["VpcId"]

    def delete(self):
        return self.client.delete_vpc(
            VpcId=self.id,
        )

    def create_subnet(self, name: str, cidr: str, availability_zone: str = "", **kwargs) -> Subnet:
        subnet = Subnet(name, self.id, cidr, availability_zone, **kwargs)
        self.subnets.append(subnet)

        return subnet

    def attach_internet_gateway(self, internet_gateway: InternetGateway | str) -> InternetGateway:
        if type(internet_gateway) == str:
            internet_gateway = InternetGateway(internet_gateway)

        self.internet_gateway = internet_gateway

        self.client.attach_internet_gateway(
            InternetGatewayId=internet_gateway.id,
            VpcId=self.id,
        )

        return internet_gateway

    def create_route_table(self, name: str, associate_subnet: str = None, **kwargs) -> RouteTable:
        route_table = RouteTable(name, self.id, **kwargs)
        self.route_tables.append(route_table)

        if associate_subnet is not None:
            route_table.associate_subnet(associate_subnet)

        return route_table

    def create_security_group(self, name: str, description: str, **kwargs) -> SecurityGroup:
        return SecurityGroup(name, description, self.id, **kwargs)
