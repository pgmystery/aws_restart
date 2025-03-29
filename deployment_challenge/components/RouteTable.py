from enum import Enum
from typing import TYPE_CHECKING, Any

from .AWS import EC2

if TYPE_CHECKING:
    from .InternetGateway import InternetGateway
    from .NAT import NAT
    from .Subnet import Subnet


class RouteTarget(Enum):
    # DestinationPrefixListId
    VPC = "VpcEndpointId"
    TRANSIT = "TransitGatewayId"
    LOCAL_GATEWAY = "LocalGatewayId"
    CARRIER_GATEWAY = "CarrierGatewayId"
    CORE_NETWORK = "CoreNetworkArn"
    GATEWAY = "GatewayId"
    IPV6_CIDR = "DestinationIpv6CidrBlock"
    EGRESS_INTERNET_GATEWAY = "EgressOnlyInternetGatewayId"
    INSTANCE = "InstanceId"
    NETWORK_INTERFACE = "NetworkInterfaceId"
    VPC_PEERING = "VpcPeeringConnectionId"
    NAT = "NatGatewayId"


class RouteTable(EC2):
    def __init__(self, name: str, vpc_id: str, **kwargs):
        super().__init__()

        self.associations: dict = {
            "subnets": [],
            "gateways": [],
        }

        tags = kwargs["Tags"] if "Tags" in kwargs else []

        self.info: dict[str, Any] = self.client.create_route_table(
            VpcId=vpc_id,
            TagSpecifications=[
                {
                    'ResourceType': 'route-table',
                    'Tags': [
                        *tags,
                        {
                            'Key': 'Name',
                            'Value': name,
                        },
                    ]
                },
            ],
        )["RouteTable"]
        self.id: str = self.info["RouteTableId"]

    @property
    def routes(self) -> list[dict[str, str]]:
        route_tables = self.client.describe_route_tables(RouteTableIds=[self.id])["RouteTables"]

        for route_table in route_tables:
            if route_table["RouteTableId"] == self.id:
                return route_table["Routes"]

        return []

    def add_route(self, destination_cidr: str, target: dict[RouteTarget, str]):

        return self.client.create_route(
            DestinationCidrBlock=destination_cidr,
            RouteTableId=self.id,
            **target,
        )

    def add_route_internet_gateway(self, destination_cidr: str, internet_gateway: InternetGateway):
        return self.add_route(
            destination_cidr=destination_cidr,
            target={
                RouteTarget.GATEWAY.value: internet_gateway.id,
            },
        )

    def add_route_nat_gateway(self, destination_cidr: str, nat_gateway: NAT):
        return self.add_route(
            destination_cidr=destination_cidr,
            target={
                RouteTarget.NAT.value: nat_gateway.id,
            },
        )

    def associate_subnet(self, subnet: Subnet = None):
        association = self.client.associate_route_table(
            RouteTableId=self.id,
            SubnetId=subnet.id,
        )
        self.associations["subnets"].append(association)

        return association
