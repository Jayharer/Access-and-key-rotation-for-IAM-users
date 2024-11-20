import boto3
from datetime import date

from src import config


def disableLoginAndMfa(client: boto3.client, user_name: str) -> bool:
    try:
        # disable login
        resp1 = client.delete_login_profile(
            UserName=user_name)
        # disable mfa
        resp2 = client.deactivate_mfa_device(
            UserName=user_name,
            SerialNumber='arn:aws:iam::{}:mfa/{}'.format(
                config.aws_root_account_id, user_name)
        )
        return True
    except Exception as e:
        print(repr(e))
        return False


def lambda_handler(event, context):
    iam_client = boto3.client('iam')
    list_users = iam_client.list_users()
    for user in list_users['Users']:
        print(user)
        user_name = user['UserName']
        if 'PasswordLastUsed' in user.keys():
            password_last_used = (user['PasswordLastUsed']).date()
        else:
            password_last_used = (user['CreateDate']).date()
        today = date.today()
        day_difference = (today - password_last_used).days
        print(day_difference, user_name, password_last_used)
        if day_difference >= 30 or day_difference == 0:
            if disableLoginAndMfa(iam_client, user_name):
                print("login & mfa disable for {}".format(user_name))
            else:
                print("Error in login & mfa disable for {}".format(user_name))
    return {'statusCode': 200, 'msg': 'success console access'}


if __name__ == "__main__":
    lambda_handler(None, None)