from threading import Thread
from typing import Any, TYPE_CHECKING

from .AWS import EC2

if TYPE_CHECKING:
    from .Subnet import Subnet
    from .ElasticIp import ElasticIp


class NATBase:
    def __init__(self, name: str, subnet: "Subnet", allocation: "ElasticIp"):
        self.data: dict[str, Any] = {
            "name": name,
            "subnet": subnet,
            "allocation": allocation,
        }


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

    @staticmethod
    def CreateMultiple(nats_config: list[NATBase]) -> dict[str, "NAT"]:
        def create(result_dict: dict[str, "NAT"],  name: str, *args, **kwargs):
            result_dict[name] = NAT(name=name, *args, **kwargs)

        nats: dict[str, "NAT"] = {}

        threads: list[Thread] = []
        for nat_config in nats_config:
            t = Thread(target=create, kwargs={
                **nat_config.data,
                "result_dict": nats,
            })
            threads.append(t)
            t.start()

        for thread in threads:
            thread.join()

        return nats
