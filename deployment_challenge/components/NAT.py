from typing import Any, TYPE_CHECKING

from .AWS import EC2

if TYPE_CHECKING:
    from .Subnet import Subnet
    from .ElasticIp import ElasticIp


class NAT(EC2):
    def __init__(self, name: str, subnet: "Subnet", allocation: "ElasticIp", wait_till_ready: bool=True):
        super().__init__()

        self.info: dict[str, Any] = self.client.create_nat_gateway(
            AllocationId=allocation.id,
            SubnetId=subnet.id,
            TagSpecifications=[
                {
                    'ResourceType': 'natgateway',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': name
                        },
                    ]
                },
            ],
            ConnectivityType='public',
        )["NatGateway"]
        self.id: str = self.info["NatGatewayId"]

        if wait_till_ready:
            self.wait_till_ready()

    def wait_till_ready(self):
        waiter = self.client.get_waiter('nat_gateway_available')
        waiter.wait(NatGatewayIds=[self.id])
