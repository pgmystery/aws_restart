import os

import boto3
from dotenv import load_dotenv


class Credentials:
    def __init__(
        self,
        region: str,
        access_key: str,
        secret_key: str,
        session_token: str,
    ):
        self.region = region
        self.access_key = access_key
        self.secret_key = secret_key
        self.session_token = session_token


class AWSComponent:
    def __init__(self, dot_env_file_path: str = ".env"):
        load_dotenv(dotenv_path=dot_env_file_path)

        REGION = os.getenv('AWS_REGION')
        ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
        SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
        SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')

        self.credentials = Credentials(
            region=REGION,
            access_key=ACCESS_KEY,
            secret_key=SECRET_KEY,
            session_token=SESSION_TOKEN,
        )


class EC2(AWSComponent):
    def __init__(self, dot_env_file_path: str = ".env"):
        super().__init__(dot_env_file_path)

        self.client = boto3.client(
            'ec2',
            region_name=self.credentials.region,
            aws_access_key_id=self.credentials.access_key,
            aws_secret_access_key=self.credentials.secret_key,
            aws_session_token=self.credentials.session_token,
        )
