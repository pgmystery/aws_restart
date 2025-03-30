from enum import Enum
from typing import TYPE_CHECKING, Any

from .AWS import RDS

if TYPE_CHECKING:
    from .SubnetGroup import SubnetGroup
    from .SecurityGroup import SecurityGroup


class DatabaseEngine(Enum):
    AURORA_MYSQL="aurora-mysql"
    AURORA_POSTGRESQL="aurora-postgresql"
    CUSTOM_ORACLE_EE="custom-oracle-ee"
    CUSTOM_ORACLE_EE_CDB="custom-oracle-ee-cdb"
    CUSTOM_ORACLE_SE2="custom-oracle-se2"
    CUSTOM_ORACLE_SE2_CDB="custom-oracle-se2-cdb"
    CUSTOM_SQLSERVER_EE="custom-sqlserver-ee"
    CUSTOM_SQLSERVER_SE="custom-sqlserver-se"
    CUSTOM_SQLSERVER_WEB="custom-sqlserver-web"
    CUSTOM_SQLSERVER_DEV="custom-sqlserver-dev"
    DB2_AE="db2-ae"
    DB2_SE="db2-se"
    MARIADB="mariadb"
    MYSQL="mysql"
    ORACLE_EE = "oracle-ee"
    ORACLE_EE_CDB = "oracle-ee-cdb"
    ORACLE_SE2 = "oracle-se2"
    ORACLE_SE2_CDB = "oracle-se2-cdb"
    POSTGRESQL = "postgres"
    SQLSERVER_EE = "sqlserver-ee"
    SQLSERVER_SE = "sqlserver-se"
    SQLSERVER_EX = "sqlserver-ex"
    SQLSERVER_WEB = "sqlserver-web"


class Database(RDS):
    def __init__(
        self,
        name: str,
        db_engine: DatabaseEngine,
        db_engine_version: str,
        master_username: str,
        master_user_password: str,
        storage_size_gb: int,
        subnet_group: "SubnetGroup",
        security_groups: list["SecurityGroup"],
        db_instance_class: str = "db.t3.micro",
        multi_az: bool = False,
        storage_type: str = "gp2",
        **kwargs,
    ):
        super().__init__()

        self.info: dict[str, Any] = self.client.create_db_instance(
            DBInstanceIdentifier=name,
            DBInstanceClass=db_instance_class,
            Engine=db_engine.value,
            MasterUsername=master_username,
            MasterUserPassword=master_user_password,
            AllocatedStorage=storage_size_gb,
            DBSubnetGroupName=subnet_group.name,
            VpcSecurityGroupIds=[security_group.id for security_group in security_groups],
            MultiAZ=multi_az,  # Set to True for high availability (optional)
            PubliclyAccessible=True,  # Set to False if you don't want the DB to be publicly accessible (optional)
            StorageType=storage_type,  # General purpose SSD (optional)
            EngineVersion=db_engine_version,  # Specify the MySQL engine version (optional)
            MonitoringInterval=0,
            BackupRetentionPeriod=0,
            Tags=[
                    {
                        'Key': 'Name',
                        'Value': name
                    }
                ],
            **kwargs,
        )["DBInstance"]

        waiter = self.client.get_waiter('db_instance_available')
        waiter.wait(DBInstanceIdentifier=name)

        self.info = self.client.describe_db_instances(DBInstanceIdentifier=name)["DBInstances"][0]
        self.endpoint: str = self.info["Endpoint"]["Address"]
