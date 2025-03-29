from typing import Any

from .AWS import EC2


class Subnet(EC2):
    def __init__(
        self,
        name: str,
        vpc_id: str,
        cidr: str,
        availability_zone: str = "",
        **kwargs
    ):
        super().__init__()

        tags = kwargs["Tags"] if "Tags" in kwargs else []

        self.name: str = name
        self.vpcId: str = vpc_id
        self.cidr: str = cidr
        self.availability_zone: str = availability_zone
        self.info: dict[str, Any] = self.client.create_subnet(
            VpcId=vpc_id,
            AvailabilityZone=availability_zone,
            CidrBlock=cidr,
            TagSpecifications=[
                {
                    'ResourceType': "subnet",
                    'Tags': [
                        *tags,
                        {
                            'Key': 'Name',
                            'Value': name
                        },
                    ]
                },
            ],
        )["Subnet"]
        self.id: str = self.info["SubnetId"]
