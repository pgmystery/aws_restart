from .AWS import EC2


class SecurityGroup(EC2):
    def __init__(self, name: str, description: str, vpc_id: str, **kwargs) -> None:
        super().__init__()

        self.rules = []
        self.info = self.client.create_security_group(
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

        # TODO: ?
        # self.association_info = self.client.associate_security_group_vpc(
        #     GroupId=self.id,
        #     VpcId=vpc_id,
        # )

    def add_inbound_rule(
        self,
        protocol: str,
        cidr: str,
        from_port: int,
        to_port: int,
    ):
        rule = self.client.authorize_security_group_ingress(
            GroupId=self.id,
            IpProtocol=protocol,
            CidrIp=cidr,
            FromPort=from_port,
            ToPort=to_port
        )["SecurityGroupRules"]

        self.rules.append(rule)

        return rule

    def add_inbound_rule_sg(
        self,
        protocol: str,
        sg_id: str,
        from_port: int,
        to_port: int,
    ):
        rule = self.client.authorize_security_group_ingress(
            GroupId=self.id,
            IpProtocol=protocol,
            SourceSecurityGroupName=sg_id,
            FromPort=from_port,
            ToPort=to_port
        )["SecurityGroupRules"]

        self.rules.append(rule)

        return rule
