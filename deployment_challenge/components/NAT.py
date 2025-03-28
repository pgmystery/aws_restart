from .AWS import EC2


class NAT(EC2):
    def __init__(self, name: str, subnet_id: str, allocation_id: str):
        super().__init__()

        self.info = self.client.create_nat_gateway(
            AllocationId=allocation_id,
            SubnetId=subnet_id,
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
        self.id = self.info["NatGatewayId"]
