from .AWS import EC2


class InternetGateway(EC2):
    def __init__(self, name: str):
        super().__init__()

        self.name = name
        self.info = self.client.create_internet_gateway(
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
        self.id = self.info["InternetGatewayId"]
        self.owner = self.info["OwnerId"]
