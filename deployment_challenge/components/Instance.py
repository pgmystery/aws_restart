from .AWS import EC2


class Instance(EC2):
    def __init__(
        self,
        name: str,
        image_id: str,
        instance_type: str,
        key_pair: str,
        subnet_id: str,
        security_groups: list[str],
        associate_public_ip_address: bool = False,
        user_data: str = "",
        availability_zone: str = None,
    ):
        super().__init__()

        self.info = self.client.run_instances(
            ImageId=image_id,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            KeyName=key_pair,
            Placement={
                "AvailabilityZone": availability_zone
            },
            NetworkInterfaces=[
                {
                    "AssociatePublicIpAddress": associate_public_ip_address,
                    "DeviceIndex": 0,
                    "SubnetId": subnet_id,
                    "Groups": security_groups,
                },
            ],
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {"Key": "Name", "Value": name},
                    ],
                },
            ],
            UserData=user_data,
        )["Instances"][0]
        self.id = self.info["InstanceId"]

    @property
    def private_ip(self):
        self.info = self.get_info()

        if "PrivateIpAddress" not in self.info:
            return None

        return self.info["PrivateIpAddress"]

    @property
    def public_ip(self):
        self.info = self.get_info()

        if "PublicIpAddress" not in self.info:
            return None

        return self.info["PublicIpAddress"]

    def get_info(self):
        return self.client.describe_instances(InstanceIds=[self.id])['Reservations'][0]['Instances'][0]
