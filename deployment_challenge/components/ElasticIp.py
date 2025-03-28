from .AWS import EC2


class ElasticIp(EC2):
    def __init__(self, name: str):
        super().__init__()

        self.info = self.client.allocate_address(
            Domain='vpc',
            TagSpecifications=[
                {
                    'ResourceType': "elastic-ip",
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': name
                        },
                    ]
                },
            ],
        )
        self.id = self.info["AllocationId"]
        self.ip = self.info["PublicIp"]
