from typing import Any

from .AWS import EC2


class InternetGateway(EC2):
    def __init__(self, name: str):
        super().__init__()

        self.name: str = name
        self.info: dict[str, Any] = self.client.create_internet_gateway(
            TagSpecifications=[
                {
                    'ResourceType': 'internet-gateway',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': name
                        },
                    ]
                },
            ],
        )["InternetGateway"]
        self.id: str = self.info["InternetGatewayId"]
        self.owner: str = self.info["OwnerId"]
