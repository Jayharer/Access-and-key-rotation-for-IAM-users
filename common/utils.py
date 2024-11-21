import boto3
from botocore.exceptions import ClientError


def checkConsoleAccess(client: boto3.client, user_name: str) -> bool:
    # get login profile of user to identity console disable user
    try:
        resp = client.get_login_profile(UserName=user_name)
        return True
    except ClientError as e:
        return False
