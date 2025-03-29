from typing import Any, TYPE_CHECKING

from .AWS import EC2

if TYPE_CHECKING:
    from .VPC import VPC


class Subnet(EC2):
    def __init__(
        self,
        name: str,
        vpc: "VPC",
        cidr: str,
        availability_zone: str = "",
        **kwargs
    ):
        super().__init__()

        tags = kwargs["Tags"] if "Tags" in kwargs else []

        self.name: str = name
        self.vpcId: str = vpc.id
        self.cidr: str = cidr
        self.availability_zone: str = availability_zone
        self.info: dict[str, Any] = self.client.create_subnet(
            VpcId=vpc.id,
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
