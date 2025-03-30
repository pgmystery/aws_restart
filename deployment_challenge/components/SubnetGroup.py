from typing import TYPE_CHECKING, Any

from .AWS import RDS

if TYPE_CHECKING:
    from .Subnet import Subnet


class SubnetGroup(RDS):
    def __init__(self, name: str, description: str, subnets: list["Subnet"]):
        super().__init__()

        self.name: str = name
        self.subnets: list["Subnet"] = subnets

        self.info: dict[str, Any] = self.client.create_db_subnet_group(
            DBSubnetGroupName=name,
            DBSubnetGroupDescription=description,
            SubnetIds=[subnet.id for subnet in subnets],
        )["DBSubnetGroup"]
