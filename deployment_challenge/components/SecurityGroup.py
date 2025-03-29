from typing import Any

from .AWS import EC2


class SecurityGroup(EC2):
    def __init__(self, name: str, description: str, vpc_id: str, **kwargs) -> None:
        super().__init__()

        self.rules = []
        self.info: dict[str, Any] = self.client.create_security_group(
            **kwargs,
            GroupName=name,
            Description=description,
            VpcId=vpc_id,
            TagSpecifications=[
                {
                    'ResourceType': 'security-group',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': name
                        },
                    ]
                },
            ],
        )
        self.id: str = self.info["GroupId"]

    def add_inbound_rule_cidr(
        self,
        protocol: str,
        from_port: int,
        to_port: int,
        cidr: str,
    ):
        return self.add_inbound_rule(
            protocol=protocol,
            from_port=from_port,
            to_port=to_port,
            IpRanges=[{
                'CidrIp': cidr,
            }],
        )

    def add_inbound_rule_sg(
        self,
        protocol: str,
        from_port: int,
        to_port: int,
        security_group: "SecurityGroup",
    ):
        return self.add_inbound_rule(
            protocol=protocol,
            from_port=from_port,
            to_port=to_port,
            UserIdGroupPairs=[{
                'GroupId': security_group.id,
            }],
        )

    def add_inbound_rule(
        self,
        protocol: str,
        from_port: int,
        to_port: int,
        **kwargs,
    ):
        ip_permissions = [{
            'IpProtocol': protocol,
            'FromPort': from_port,
            'ToPort': to_port,
            **kwargs,
        }]

        rule = self.client.authorize_security_group_ingress(
            GroupId=self.id,
            IpPermissions=ip_permissions,
        )["SecurityGroupRules"]

        self.rules.append(rule)

        return rule
